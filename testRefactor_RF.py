from random import randint
import ufoProcessor
import ufoProcessor.ufoOperator
import importlib
importlib.reload(ufoProcessor.ufoOperator)
#print(ufoProcessor.__file__)
ds5Path = "/Users/erik/code/type2/Principia/sources/Principia_wdth.designspace"
ds5Path = "/Users/erik/code/type2/Principia/sources/Principia_wght_wght.designspace"
#ds5Path = "/Users/erik/code/ufoProcessor/Tests/ds5/ds5.designspace"

doc = ufoProcessor.ufoOperator.UFOOperator(ds5Path, useVarlib=False, debug=False)
doc.loadFonts()
#doc.generateUFOs()

def ip(a, b, f):
    return a+f*(b-a)
    
font = CurrentFont()

loc = doc.newDefaultLocation()
loc['width'] = randint(50, 100)
#print(loc)

# make some tests at different layers
randomloc = doc.randomLocation(0.03, anisotropic=True)
#print(randomloc)
test = [
    ("foreground", doc.randomLocation(0.03, anisotropic=True), False),
    ("background", doc.randomLocation(0.03, anisotropic=True), False),
    # ("random_width_inter_MM", dict(width=randint(50,100), italic=1), False),
    # ("random_width_xtr_MM", dict(width=randint(10,150), italic=1), False),
    # ("random_width_xtr_narrow_VL", dict(width=randint(10,50), italic=1), True),
    # ("random_width_xtr_wide_VL", dict(width=randint(100,500), italic=1), True),

    # ("10_width_xtr_VL", dict(width=10, italic=1), True),
    # ("10_width_xtr_MM", dict(width=10, italic=1), False),
    # ("200_width_xtr_wide_VL", dict(width=200, italic=1), True),
    # ("200_width_xtr_wide_MM", dict(width=200, italic=1), False),

    # ("aniso_width_inter_MM", dict(width=(50,100), italic=0), False),
    # ("aniso_width_inter_VL", dict(width=(50,100), italic=0), True),

    # ("aniso_width_xtra_MM", dict(width=(-50,200), italic=0), False),
    # ("aniso_width_xtra_VL", dict(width=(-50,200), italic=0), True),

    ]

g = CurrentGlyph()
dstName = g.name

useVarlib = False
for layerName, loc, _ in test:
    res = doc.makeOneGlyph(dstName, location=loc, bend=True, decomposeComponents=False, useVarlib=useVarlib, roundGeometry=True)
    dst = font[dstName].getLayer(layerName)
    dst.clear()
    if res is not None:
        res.guidelines = []     # delete guidelines in mathglyph until fontparts issue is solved
        dst.fromMathGlyph(res)
        dst.width = max(0, res.width)
    
    #print(len(dst.components))
    for comp in dst.components:
        #print("-- processing baseglyph", comp.baseGlyph)
        res2 = doc.makeOneGlyph(comp.baseGlyph, location=loc, bend=True, decomposeComponents=False, useVarlib=useVarlib, roundGeometry=True)
        # let's make sure the glyph exists in the layer
        #print('layerName:', layerName)
        dstLayer = font.getLayer(layerName)
        if not comp.baseGlyph in dstLayer:
            dstLayer.newGlyph(comp.baseGlyph)
        dst2 = dstLayer[comp.baseGlyph]
        dst2.clear()
        #print('dst.anchors:', dst.anchors)
        #print('dst.guidelines:', dst.guidelines)
        for item in res2.guidelines:
            print(item)
        res2.guidelines = []     # delete guidelines in mathglyph until fontparts issue is solved
        #print('dst.guidelines:', res2.guidelines)
        dst2.fromMathGlyph(res2)
        dst2.width = max(0, res2.width)

        dst2.update()
    dst.update()

ufoProcessor.ufoOperator.inspectMemoizeCache()
