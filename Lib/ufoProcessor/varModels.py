from fontTools.designspaceLib import AxisDescriptor
from fontTools.varLib.models import VariationModel, normalizeLocation

# a thing that looks like a mutator on the outside, but uses the fonttools varilb logic.
# which is different from the mutator.py implementation.

class VarModelBender(object):
    def __init__(self, axes):
        # axes: list of axis dictionaries, not axisdescriptor objects.
        self.axisOrder = [a['name'] for a in axes]
        self.axes = {}
        self.models = {}
        self.values = {}
        for a in axes:
            self.axes[a['name']] = (a['minimum'], a['default'], a['maximum'])
        self.models = {}
        for a in axes:
            mapData = a.get('map', [])
            self._makeWarpFromList(a['name'], mapData)

    def _makeWarpFromList(self, axisName, mapData):
        # check for the extremes, add if necessary
        minimum, default, maximum = self.axes[axisName]
        if not sum([a==minimum for a, b in mapData]):
            mapData = [(minimum,minimum)] + mapData
        if not sum([a==maximum for a, b in mapData]):
            mapData.append((maximum,maximum))
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
            #print('values', values)

            value = self.models[axisName].interpolateFromMasters(bLoc, values)
            #print(value)
            new[axisName] = value
        return new


class VariationModelMutator(object):
    def __init__(self, items, axes, model=None):
        # items: list of locationdict, value tuples
        # axes: list of axis dictionaries, not axisdescriptor objects.
        # model: a model, if we want to share one
        self.axisOrder = [a['name'] for a in axes]
        self.bender = VarModelBender(axes)
        self.axes = {}
        for a in axes:
            self.axes[a['name']] = (a['minimum'], a['default'], a['maximum'])
        if model is None:
            self.model = VariationModel([self._normalize(a) for a,b in items], axisOrder=self.axisOrder)
        else:
            self.model = model
        self.masters = [b for a, b in items]

    def get(self, key):
        if key in self.model.locations:
            i = self.model.locations.index(key)
            return self.masters[i]
            
    def getFactors(self, location):
        nl = self._normalize(location)
        return self.model.getScalars(nl)

    def makeInstance(self, location, bend=False):
        # check for anisotropic locations here
        if bend:
            location = self.bender(location)
        location = self._normalize(location)
        return self.model.interpolateFromMasters(location, self.masters)

    def _normalize(self, location):
        return normalizeLocation(location, self.axes)

if __name__ == "__main__":
    a = AxisDescriptor()
    a.name = "A"
    a.tag = "A___"
    a.minimum = 0
    a.default = 0
    a.maximum = 100
    #a.map = ((a.minimum,a.minimum),(500, 250),(a.maximum,a.maximum))
    a.map = [(50, 25), (60, 35)]

    b = AxisDescriptor()
    b.name = "B"
    b.tag = "B___"
    b.minimum = -100
    b.default = 10
    b.maximum = 110
    axes = [a.serialize(),b.serialize()]

    items = [
        ({}, 0),
        #({'A': 50, 'B': 50}, 10),
        ({'A': 100}, 10),
        ({'B': 100}, 10),
        ({'B': -100}, 0-10),
        #({'A': 100, 'B': 100}, 0),
        #({'A': 55, 'B': 75}, 1),
        #({'A': 65, 'B': 99}, 1),
    ]

    mm = VariationModelMutator(items, axes)

    print(mm.makeInstance(dict(A=0, B=0)))
    print(mm.makeInstance(dict(A=100, B=0)))
    print(mm.makeInstance(dict(A=0, B=100)))
    print(mm.makeInstance(dict(A=100, B=100)))
    print(1, mm.makeInstance(dict(A=50, B=0)))
    print(2, mm.makeInstance(dict(A=50, B=0),bend=True))

    # assert mm.makeInstance(dict(A=0, B=0)) == 0
    # assert mm.makeInstance(dict(A=100, B=0)) == 10
    # assert mm.makeInstance(dict(A=0, B=100)) == 10
    # assert mm.makeInstance(dict(A=100, B=100)) == 0
    # assert mm.makeInstance(dict(A=50, B=0),bend=False) == 5
    # assert mm.makeInstance(dict(A=50, B=0),bend=True) == 2.5

    # # do we support axismaps?
    # vmb = VarModelBender(axes=axes)
    # for v in range(0, 110, 10):
    #     print(v, vmb(dict(A=v)))
    # for v in range(0, 130, 10):
    #     print(v, vmb(dict(B=v)))
    # for v in range(0, 130, 10):
    #     print(v, vmb(dict(A=v, B=v)))
