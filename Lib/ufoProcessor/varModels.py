# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import
from fontTools.varLib.models import VariationModel, normalizeLocation

# process the axis map values
class AxisMapper(object):
    def __init__(self, axes):
        # axes: list of axis axisdescriptors
        self.axisOrder = [a.name for a in axes]
        self.axes = {}
        self.models = {}
        self.values = {}
        self.models = {}
        for a in axes:
            self.axes[a.name] = (a.minimum, a.default, a.maximum)
        for a in axes:
            mapData = a.map
            if mapData:
                self._makeWarpFromList(a.name, mapData)

    def _makeWarpFromList(self, axisName, mapData):
        # check for the extremes, add if necessary
        minimum, default, maximum = self.axes[axisName]
        if not sum([a==minimum for a, b in mapData]):
            mapData = [(minimum,minimum)] + mapData
        if not sum([a==maximum for a, b in mapData]):
            mapData.append((maximum,maximum))
        if not (default, default) in mapData:
            mapData.append((default, default))

        mapLocations = []
        mapValues = []
        for x, y in mapData:
            l = normalizeLocation(dict(w=x), dict(w=[minimum,default,maximum]))
            mapLocations.append(l)
            mapValues.append(y)
        self.models[axisName] = VariationModel(mapLocations, axisOrder=['w'])
        self.values[axisName] = mapValues

    def _normalize(self, location):
        new = {}
        for axisName in location.keys():
            new[axisName] = normalizeLocation(dict(w=location[axisName]), dict(w=self.axes[axisName]))
        return new

    def __call__(self, location):
        # bend a location according to the defined warps
        nl = self._normalize(location) # ugh!
        new = location.copy()
        for axisName in location.keys():
            if not axisName in self.models:
                continue
            bLoc = nl[axisName]
            values = self.values[axisName]
            value = self.models[axisName].interpolateFromMasters(bLoc, values)
            new[axisName] = value
        return new


class VariationModelMutator(object):
    """ a thing that looks like a mutator on the outside,
        but uses the fonttools varlib logic to calculate.
    """

    def __init__(self, items, axes, model=None):
        # items: list of locationdict, value tuples
        # axes: list of axis dictionaried, not axisdescriptor objects.
        # model: a model, if we want to share one
        self.axisOrder = [a.name for a in axes]
        self.axisMapper = AxisMapper(axes)
        self.axes = {}
        for a in axes:
            self.axes[a.name] = (a.minimum, a.default, a.maximum)
        if model is None:
            self.model = VariationModel([self._normalize(a) for a,b in items], axisOrder=self.axisOrder)
        else:
            self.model = model
        self.masters = [b for a, b in items]
        self.locations = [a for a, b in items]

    def get(self, key):
        if key in self.model.locations:
            i = self.model.locations.index(key)
            return self.masters[i]
        return None

    def getFactors(self, location):
        nl = self._normalize(location)
        return self.model.getScalars(nl)

    def getMasters(self):
        return self.masters

    def getSupports(self):
        return self.model.supports

    def getReach(self):
        items = []
        for supportIndex, s in enumerate(self.getSupports()):
            sortedOrder = self.model.reverseMapping[supportIndex]
            print(self.masters[sortedOrder], s)
            print(self.locations[sortedOrder])
            items.append((self.masters[sortedOrder], s))
        return items


    def makeInstance(self, location, bend=True):
        # check for anisotropic locations here
        if bend:
            location = self.axisMapper(location)
        nl = self._normalize(location)
        return self.model.interpolateFromMasters(nl, self.masters)

    def _normalize(self, location):
        return normalizeLocation(location, self.axes)


if __name__ == "__main__":
    from fontTools.designspaceLib import AxisDescriptor
    a = AxisDescriptor()
    a.name = "A"
    a.tag = "A___"
    a.minimum = -100
    a.default = 0
    a.maximum = 100
    a.map = [(-50, 25), (50, 25), (60, 35)]

    b = AxisDescriptor()
    b.name = "B"
    b.tag = "B___"
    b.minimum = 0
    b.default = 50
    b.maximum = 100
    axes = [a,b]
    
    items = [
        ({}, 0),
        #({'A': 50, 'B': 50}, 10),
        ({'A': 100}, 10),
        ({'B': 100}, 10),
        #({'B': -100}, -10),    # this will fail, no extrapolating
        ({'A': 100, 'B': 100}, 0),
        ({'A': 55, 'B': 75}, 1),
        ({'A': 65, 'B': 99}, 1),
    ]

    am = AxisMapper(axes)
    assert am(dict(A=0)) == {'A': 0.0}
    assert am(dict(A=50)) == {'A': 25.0}    # one of the steps
    assert am(dict(A=55)) == {'A': 30.000000000000004}
    assert am(dict(A=60)) == {'A': 35.0}
    assert am(dict(A=80)) == {'A': 67.50000000000001}
    assert am(dict(A=100)) == {'A': 100.0}

    mm = VariationModelMutator(items, axes)

    assert mm.makeInstance(dict(A=0, B=0)) == 0
    assert mm.makeInstance(dict(A=100, B=0)) == 10
    assert mm.makeInstance(dict(A=0, B=100)) == 10
    assert mm.makeInstance(dict(A=100, B=100)) == 0
    assert mm.makeInstance(dict(A=50, B=0),bend=False) == 5
    assert mm.makeInstance(dict(A=50, B=0),bend=True) == 2.5

    mm.getReach()