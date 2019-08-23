# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import
from fontTools.varLib.models import VariationModel, normalizeLocation


# alternative axisMapper that uses map_forward and map_backward from fonttools

class AxisMapper(object):
    def __init__(self, axes):
        # axes: list of axis axisdescriptors
        self.axisOrder = [a.name for a in axes]
        self.axisDescriptors = {}
        for a in axes:
            self.axisDescriptors[a.name] = a

    def getMappedAxisValues(self):
        values = {}
        for axisName in self.axisOrder:
            a = self.axisDescriptors[axisName]
            values[axisName] = a.map_forward(a.minimum), a.map_forward(a.default), a.map_forward(a.maximum)
        return values

    def __call__(self, location):
        return self.map_forward(location)

    def map_backward(self, location):
        new = {}
        for axisName in location.keys():
            if not axisName in self.axisOrder:
                continue
            if axisName not in location:
                continue
            new[axisName] = self.axisDescriptors[axisName].map_backward(location[axisName])
        return new

    def map_forward(self, location):
        new = {}
        for axisName in location.keys():
            if not axisName in self.axisOrder:
                continue
            if axisName not in location:
                continue
            new[axisName] = self.axisDescriptors[axisName].map_forward(location[axisName])
        return new

# process the axis map values
# class AxisMapper(object):
#     def __init__(self, axes):
#         # axes: list of axis axisdescriptors
#         self.axisOrder = [a.name for a in axes]
#         self.axes = {}
#         self.models = {}
#         self.values = {}
#         self.models = {}
#         for a in axes:
#             self.axes[a.name] = (a.minimum, a.default, a.maximum)
#         for a in axes:
#             mapData = a.map
#             if mapData:
#                 self._makeWarpFromList(a.name, mapData)

#     def _makeWarpFromList(self, axisName, mapData):
#         # check for the extremes, add if necessary
#         # https://github.com/fonttools/fonttools/issues/1655
#         # assume minimum, default and maximum values to be in user coordinates.

#         #if not sum([a==minimum for a, b in mapData]):
#         #    mapData = [(minimum,minimum)] + mapData
#         #if not sum([a==maximum for a, b in mapData]):
#         #    mapData.append((maximum,maximum))
#         #if not (default, default) in mapData:
#         #    mapData.append((default, default))

#         mapLocations = []
#         mapValues = []
#         for x, y in mapData:
#             l = normalizeLocation(dict(w=x), dict(w=[minD,defD,maxD]))
#             mapLocations.append(l)
#             mapValues.append(y)
#         self.models[axisName] = VariationModel(mapLocations, axisOrder=['w'])
#         self.values[axisName] = mapValues

#     def _normalize(self, location):
#         new = {}
#         for axisName in location.keys():
#             new[axisName] = normalizeLocation(dict(w=location[axisName]), dict(w=self.axes[axisName]))
#         return new

#     def __call__(self, location):
#         # bend a location according to the defined warps
#         nl = self._normalize(location) # ugh!
#         new = location.copy()
#         for axisName in location.keys():
#             if not axisName in self.models:
#                 continue
#             bLoc = nl[axisName]
#             values = self.values[axisName]
#             value = self.models[axisName].interpolateFromMasters(bLoc, values)
#             new[axisName] = value
#         return new


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
            dd = [self._normalize(a) for a,b in items]
            ee = self.axisOrder
            self.model = VariationModel(dd, axisOrder=ee)
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
            #print("getReach", self.masters[sortedOrder], s)
            #print("getReach", self.locations[sortedOrder])
            items.append((self.masters[sortedOrder], s))
        return items


    def makeInstance(self, location, bend=False):
        # check for anisotropic locations here
        #print("\t1", location)
        if bend:
            location = self.axisMapper(location)
        #print("\t2", location)
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
    a.map = [(-100, 40), (100, 50)]

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
        ({'A': -100}, 10),
        ({'B': 100}, -10),
        #({'B': -100}, -10),    # this will fail, no extrapolating
        ({'A': 100, 'B': 100}, 22),
        #({'A': 55, 'B': 75}, 1),
        #({'A': 65, 'B': 99}, 1),
    ]

    am = AxisMapper(axes)
    #assert am(dict(A=0)) == {'A': 45}
    print(am(dict(A=100, B=None)))
    #assert am(dict(A=0, B=100)) == {'A': 45}

    # mm = VariationModelMutator(items, axes)

    # assert mm.makeInstance(dict(A=0, B=0)) == 0
    # assert mm.makeInstance(dict(A=100, B=0)) == 10
    # assert mm.makeInstance(dict(A=0, B=100)) == 10
    # assert mm.makeInstance(dict(A=100, B=100)) == 0
    # assert mm.makeInstance(dict(A=50, B=0),bend=False) == 5
    # assert mm.makeInstance(dict(A=50, B=0),bend=True) == 2.5

    # mm.getReach()

    

    a = AxisDescriptor()
    a.name = "Weight"
    a.tag = "wght"
    a.minimum = 300
    a.default = 300
    a.maximum = 600
    a.map = ((300,0), (600,1000))

    b = AxisDescriptor()
    b.name = "Width"
    b.tag = "wdth"
    b.minimum = 200
    b.default = 800
    b.maximum = 800
    b.map = ((200,5), (800,10))
    axes = [a,b]
    
    aam = AxisMapper(axes)
    print(aam(dict(Weight=0, Width=0)))
    print(aam.getMappedAxisValues())

    print('1', aam.map_forward({'Weight': 0}))

    # fine. sources are in user values. Progress.
    items = [
        ({}, 13),
        ({'Weight': 300, 'Width': 200}, 20),
        ({'Weight': 600, 'Width': 800}, 60),
    ]

    mm = VariationModelMutator(items, axes)
    print("_normalize", mm._normalize(dict(Weight=0, Width=1000)))
    # oh wow, master locations need to be in user coordinates!?
    assert mm.makeInstance(dict()) == 13
    assert mm.makeInstance(dict(Weight=300, Width=800)) == 13


    l = dict(Weight=400, Width=200)
    lmapped = aam(l)
    print('0 loc', l)
    print('0 loc mapped', lmapped)
    print('1 with map', mm.makeInstance(l, bend=True))
    print('1 without map', mm.makeInstance(l, bend=False))
    print('2 with map', mm.makeInstance(lmapped, bend=True))
    print('2 without map', mm.makeInstance(lmapped, bend=False))
