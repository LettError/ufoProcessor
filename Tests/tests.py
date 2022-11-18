# standalone test
import shutil
import os
#from defcon.objects.font import Font
import logging
from ufoProcessor import *
import fontParts.fontshell


# new place for ufoProcessor tests.
# Run in regular python of choice, not ready for pytest just yet. 
# You may ask "why not?" - you may ask indeed.

# Now based on fontParts.

def addGlyphs(font, s, addSupportLayer=True):
    # we need to add the glyphs
    step = 0
    for n in ['glyphOne', 'glyphTwo', 'glyphThree', 'glyphFour', 'glyphFive']:
        font.newGlyph(n)
        g = font[n]
        p = g.getPen()
        p.moveTo((0,0))
        p.lineTo((s,0))
        p.lineTo((s,s))
        p.lineTo((0,s))
        p.closePath()
        g.move((0,s+step))
        g.width = s
        step += 50
    for n, w in [('wide', 800), ('narrow', 100)]:
        font.newGlyph(n)
        g = font[n]
        p = g.getPen()
        p.moveTo((0,0))
        p.lineTo((w,0))
        p.lineTo((w,font.info.ascender))
        p.lineTo((0,font.info.ascender))
        p.closePath()
        g.width = w
        g.appendAnchor("top", (0, w))

    if addSupportLayer:
        font.newLayer('support')
        print(n for n in font.layers if n.name == 'support')
        layer = font.getLayer('support')
        layer.newGlyph('glyphFive')
        layer.newGlyph('glyphOne')  # add an empty glyph to see how it is treated
        lg = layer['glyphFive']
        p = lg.getPen()
        w = 10
        y = -400
        p.moveTo((0,y))
        p.lineTo((s,y))
        p.lineTo((s,y+100))
        p.lineTo((0,y+100))
        p.closePath()
        lg.width = s

    font.newGlyph("wide.component")
    g = font["wide.component"]
    g.appendComponent("wide", offset=(0,0))
    #comp = g.instantiateComponent()
    #comp.baseGlyph = "wide"
    #comp.offset = (0,0)
    #g.appendComponent(comp)
    g.width = font['wide'].width
    font.newGlyph("narrow.component")
    g = font["narrow.component"]
    g.appendComponent("narrow", offset=(0,0))
    #comp = g.instantiateComponent()
    #comp.baseGlyph = "narrow"
    #comp.offset = (0,0)
    #g.appendComponent(comp)
    g.width = font['narrow'].width
    uniValue = 200
    for g in font:
        g.unicode = uniValue
        uniValue += 1


def fillInfo(font):
    font.info.unitsPerEm = 1000
    font.info.ascender = 800
    font.info.descender = -200

def _makeTestFonts(rootPath):
    """ Make some test fonts that have the kerning problem."""
    path1 = os.path.join(rootPath, "masters", "geometryMaster1.ufo")
    path2 = os.path.join(rootPath, "masters", "geometryMaster2.ufo")
    path3 = os.path.join(rootPath, "instances", "geometryInstance%3.3f.ufo")
    path4 = os.path.join(rootPath, "anisotropic_instances", "geometryInstanceAnisotropic1.ufo")
    path5 = os.path.join(rootPath, "anisotropic_instances", "geometryInstanceAnisotropic2.ufo")
    for path in [path1, path2, path3, path4, path5]:
        d = os.path.dirname(path)
        if not os.path.exists(d):
            os.makedirs(d)
    f1 = fontParts.fontshell.RFont()
    fillInfo(f1)
    addGlyphs(f1, 100, addSupportLayer=False)
    f1.features.text = u"# features text from master 1"
    f2 = fontParts.fontshell.RFont()
    fillInfo(f2)
    addGlyphs(f2, 500, addSupportLayer=True)
    f2.features.text = u"# features text from master 2"
    f1.info.ascender = 400
    f1.info.descender = -200
    f2.info.ascender = 600
    f2.info.descender = -100
    f1.info.copyright = u"This is the copyright notice from master 1"
    f2.info.copyright = u"This is the copyright notice from master 2"
    f1.lib['ufoProcessor.test.lib.entry'] = "Lib entry for master 1"
    f2.lib['ufoProcessor.test.lib.entry'] = "Lib entry for master 2"

    f1.groups["public.kern1.groupA"] = ['glyphOne', 'glyphTwo']
    f1.groups["public.kern2.groupB"] = ['glyphThree', 'glyphFour']
    f2.groups.update(f1.groups)

    f1.kerning[('public.kern1.groupA', 'public.kern2.groupB')] = -100
    f2.kerning[('public.kern1.groupA', 'public.kern2.groupB')] = -200

    f1.kerning[('glyphOne', 'glyphOne')] = -100
    f2.kerning[('glyphOne', 'glyphOne')] = 0
    f1.kerning[('glyphOne', 'glyphThree')] = 10
    f1.kerning[('glyphOne', 'glyphFour')] = 10
    # exception
    f2.kerning[('glyphOne', 'glyphThree')] = 1
    f2.kerning[('glyphOne', 'glyphFour')] = 0
    print([l.name for l in f1.layers], [l.name for l in f2.layers])

    f1.save(path1, 3)
    f2.save(path2, 3)
    return path1, path2, path3, path4, path5

def _makeSwapFonts(rootPath):
    """ Make some test fonts that have the kerning problem."""
    path1 = os.path.join(rootPath, "Swap.ufo")
    path2 = os.path.join(rootPath, "Swapped.ufo")
    f1 = fontParts.fontshell.RFont()
    fillInfo(f1)
    addGlyphs(f1, 100)
    f1.features.text = u"# features text from master 1"
    f1.info.ascender = 800
    f1.info.descender = -200
    f1.kerning[('glyphOne', 'glyphOne')] = -10
    f1.kerning[('glyphTwo', 'glyphTwo')] = 10
    f1.save(path1, 2)
    return path1, path2

def _makeTestDocument(docPath, useVarlib=True):
    # make the test fonts and a test document
    if useVarlib:
        extension = "varlib"
    else:
        extension = "mutator"
    testFontPath = os.path.join(os.getcwd(), "automatic_testfonts_%s" % extension)
    m1, m2, i1, anisotropicInstancePath1, anisotropicInstancePath2 = _makeTestFonts(testFontPath)
    d = DesignSpaceProcessor(useVarlib=useVarlib)
    a = AxisDescriptor()
    a.name = "pop"
    a.minimum = 0
    a.maximum = 1000
    a.default = 0
    a.tag = "pop*"
    a.map = [(0,0),(500,250),(1000,1000)]
    d.addAxis(a)

    s1 = SourceDescriptor()
    s1.path = m1
    s1.location = dict(pop=a.default)
    s1.name = "test.master.1"
    s1.copyInfo = True
    s1.copyFeatures = True
    s1.copyLib = True
    d.addSource(s1)

    s2 = SourceDescriptor()
    s2.path = m2
    s2.location = dict(pop=1000)
    s2.name = "test.master.2"
    d.addSource(s2)

    s3 = SourceDescriptor()
    s3.path = m2
    s3.location = dict(pop=500)
    s3.name = "test.master.support.1"
    s3.layerName = "support"
    d.addSource(s3)

    d.findDefault()
    
    for counter in range(3):
        factor = counter / 2        
        i = InstanceDescriptor()
        v = a.minimum+factor*(a.maximum-a.minimum)
        i.path = i1 % v
        i.familyName = "TestFamily"
        i.styleName = "TestStyle_pop%3.3f" % (v)
        i.name = "%s-%s" % (i.familyName, i.styleName)
        i.location = dict(pop=v)
        i.info = True
        i.kerning = True
        if counter == 2:
            i.glyphs['glyphTwo'] = dict(name="glyphTwo", mute=True)
            i.copyLib = True
        if counter == 2:
           i.glyphs['narrow'] = dict(instanceLocation=dict(pop=400), unicodes=[0x123, 0x124, 0x125])
        d.addInstance(i)

    # add anisotropic locations
    i = InstanceDescriptor()
    v = a.minimum+0.5*(a.maximum-a.minimum)
    i.path = anisotropicInstancePath1
    i.familyName = "TestFamily"
    i.styleName = "TestStyle_pop_anisotropic1"
    i.name = "%s-%s" % (i.familyName, i.styleName)
    i.location = dict(pop=(1000, 0))
    i.info = True
    i.kerning = True
    d.addInstance(i)

    i = InstanceDescriptor()
    v = a.minimum+0.5*(a.maximum-a.minimum)
    i.path = anisotropicInstancePath2
    i.familyName = "TestFamily"
    i.styleName = "TestStyle_pop_anisotropic2"
    i.name = "%s-%s" % (i.familyName, i.styleName)
    i.location = dict(pop=(0, 1000))
    i.info = True
    i.kerning = True
    d.addInstance(i)

    # add data to the document lib
    d.lib['ufoprocessor.testdata'] = dict(width=500, weight=500, name="This is a named location, stored in the document lib.")

    d.write(docPath)

def _testGenerateInstances(docPath, useVarlib=True):
    # execute the test document
    d = DesignSpaceProcessor(useVarlib=useVarlib)
    d.read(docPath)
    d.generateUFO()
    if d.problems:
        for p in d.problems:
            print("\t",p)

def testUnicodes(docPath, useVarlib=True):
    # after executing testSwap there should be some test fonts
    # let's check if the unicode values for glyph "narrow" arrive at the right place.
    d = DesignSpaceProcessor(useVarlib=useVarlib)
    d.read(docPath)
    for instance in d.instances:
        if os.path.exists(instance.path):
            f = fontParts.fontshell.RFont(instance.path)
            print("instance.path", instance.path)
            print("instance.name", instance.name, "f['narrow'].unicodes", f['narrow'].unicodes)
            #if instance.name == "TestFamily-TestStyle_pop1000.000":
            #    assert f['narrow'].unicodes == [291, 292, 293]
            #else:
            #    #assert f['narrow'].unicodes == [207]
        else:
            print("Missing test font at %s" % instance.path)

selfTest = True
if selfTest:
    for extension in ['varlib', 'mutator']:
        print("\n\n", extension)
        USEVARLIBMODEL = extension == 'varlib'
        testRoot = os.path.join(os.getcwd(), "automatic_testfonts_%s" % extension)
        if os.path.exists(testRoot):
            shutil.rmtree(testRoot)
        docPath = os.path.join(testRoot, "automatic_test.designspace")
        _makeTestDocument(docPath, useVarlib=USEVARLIBMODEL)
        _testGenerateInstances(docPath, useVarlib=USEVARLIBMODEL)

        _makeTestDocument(docPath, useVarlib=USEVARLIBMODEL)
        _testGenerateInstances(docPath, useVarlib=USEVARLIBMODEL)
        testUnicodes(docPath, useVarlib=USEVARLIBMODEL)
