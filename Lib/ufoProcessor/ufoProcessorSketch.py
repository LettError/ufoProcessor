## caching
import functools


_memoizeCache = dict()


def memoize(function):
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):        
        key = (function.__name__, self, args, tuple((key, kwargs[key]) for key in sorted(kwargs.keys())))
        if key in _memoizeCache:
            return _memoizeCache[key]
        else:
            result = function(self, *args, **kwargs)
            _memoizeCache[key] = result
            return result
    return wrapper


#####

from fontTools.designspaceLib import DesignSpaceDocument


class DesignSpaceProcessor(DesignSpaceDocument):
        
    @memoize
    def getGlyphMutator(self, glyphName, decomposeComponents=False, **discreteLocation):
        glyphs = self.collectSourcesForGlyph(glyphName, decomposeComponents=decomposeComponents, **discreteLocation)
        
        print("build for glyphName", glyphName, discreteLocation)
        return "a mutator"
    
    @memoize
    def collectSourcesForGlyph(self, glyphName, decomposeComponents=False, **discreteLocation):
        discreteLocation = self.buildDiscreteLocation(discreteLocation)
        sources = self.findSourcesForDiscreteLocation(**discreteLocation)
        return []
        
    @memoize
    def findSourcesForDiscreteLocation(self, **discreteLocation):
        discreteLocation = self.buildDiscreteLocation(discreteLocation)
        sources = []
        for source in self.sources:      
            # check if part of a dict is inside an other dict  
            if discreteLocation.items() <= source.designLocation.items():
                sources.append(source)                    
        return sources
    
    def buildDiscreteLocation(self, partialDiscretelocation):
        return {**self.getDiscreteDefaultLocation(), **partialDiscretelocation}
    
    @property
    def discreteAxes(self):
        return [axis for axis in self.axes if hasattr(axis, "values")]
        
    def getDiscreteDefaultLocation(self):
        discreteDefault = dict()
        for axis in self.discreteAxes:            
            discreteDefault[axis.name] = axis.default
        return discreteDefault
    
    def getDiscreteLocations(self):
        for axis in self.discreteAxes:
            print(axis)
    
    # chaching tools
    
    def changed(self):
        _memoizeCache.clear()
    
    def glyphChanged(self, glyphName):
        for key in list(_memoizeCache.keys()):            
            if key[0] in ("getGlyphMutator", "collectSourcesForGlyph") and key[1] == glyphName:
                del _memoizeCache[key]
        
        

d = DesignSpaceProcessor()
ds5Path = "../../Tests/202206 discrete spaces/test.ds5.designspace"
d.read(ds5Path)
r = d.getGlyphMutator("a", italic=0)
print(r)

r = d.getGlyphMutator("a", italic=0)
print(r)
r = d.getGlyphMutator("a", italic=1)
print(r)

print(d.getDiscreteDefaultLocation())

print(d.findSourcesForDiscreteLocation(countedItems=1))
print(d.getDiscreteLocations())