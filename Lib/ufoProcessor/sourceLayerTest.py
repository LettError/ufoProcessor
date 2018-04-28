# sourceLayerTi
import importlib

myFontToolsPath = "/Users/erik/code/fonttools/Lib/"
import sys
sys.path.insert(1, myFontToolsPath)


import fontTools
print("fontTools.__file__:", fontTools.__file__)
import ufoProcessor
print("ufoProcessor.__file__:", ufoProcessor.__file__)
import ufoProcessor.designspaceLib    # import DesignSpaceDocument, SourceDescriptor, InstanceDescriptor, AxisDescriptor, RuleDescriptor, processRules
print("ufoProcessor.designspaceLib.__file__:", ufoProcessor.designspaceLib.__file__)


from mutatorMath import Location

ufoPath = "sourceLayerTest/SourceLayerTest.ufo"
dsPath = "sourceLayerTest/sourceLayerTest.designspace"

ds = ufoProcessor.DesignSpaceProcessor()
ds.read(dsPath)

locs = []

for d in ds.sources:
    print(d.layerName)
    locs.append(d.location)

for d in ds.instances:
    locs.append(d.location)

ds.loadFonts()
mut = ds.getGlyphMutator("A")


for m in locs:
    loc = Location(m)
    print(loc, mut.makeInstance(loc).width)

ds.generateUFO()

print("done")