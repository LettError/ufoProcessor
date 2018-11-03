# standalone test
import shutil
import os
import defcon.objects.font
import fontParts.fontshell.font
import logging
from ufoProcessor import *


# new place for ufoProcessor tests.
# Run in regular python of choice, not ready for pytest just yet. 
# You may ask "why not?" - you may ask indeed.

# make the tests work with defcon as well as fontparts

def addExtraGlyph(font, name, s=200):
    font.newGlyph(name)
    g = font[name]
    p = g.getPen()
    p.moveTo((0,0))
    p.lineTo((s,0))
    p.lineTo((s,s))
    p.lineTo((0,s))
    p.closePath()
    g.width = s

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

    if addSupportLayer:
        font.newLayer('support')
        layer = font.layers['support']
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
    comp = g.instantiateComponent()
    comp.baseGlyph = "wide"
    comp.offset = (0,0)
    g.appendComponent(comp)
    g.width = font['wide'].width
    font.newGlyph("narrow.component")
    g = font["narrow.component"]
    comp = g.instantiateComponent()
    comp.baseGlyph = "narrow"
    comp.offset = (0,0)
    g.appendComponent(comp)
    g.width = font['narrow'].width
    uniValue = 200
    for g in font:
        g.unicode = uniValue
        uniValue += 1


def fillInfo(font):
    font.info.unitsPerEm = 1000
    font.info.ascender = 800
    font.info.descender = -200

def _create_parent_dir(ufo_path):
    """
    Creates the parent directory where the UFO will be saved, in case it
    doesn't exist already. This is required because fontTools.ufoLib no
    longer calls os.makedirs.
    """
    directory = os.path.dirname(os.path.normpath(ufo_path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def _makeTestFonts(rootPath):
    """ Make some test fonts that have the kerning problem."""
    path1 = os.path.join(rootPath, "masters", "geometryMaster1.ufo")
    path2 = os.path.join(rootPath, "masters", "geometryMaster2.ufo")
    path3 = os.path.join(rootPath, "instances", "geometryInstance%3.3f.ufo")
    path4 = os.path.join(rootPath, "anisotropic_instances", "geometryInstanceAnisotropic1.ufo")
    path5 = os.path.join(rootPath, "anisotropic_instances", "geometryInstanceAnisotropic2.ufo")
    f1 = Font()
    fillInfo(f1)
    addGlyphs(f1, 100, addSupportLayer=False)
    addExtraGlyph(f1, "extra.glyph.for.neutral")
    f1.features.text = u"# features text from master 1"
    f2 = Font()
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

    _create_parent_dir(path1)
    _create_parent_dir(path2)
    f1.save(path1, 3)
    f2.save(path2, 3)
    return path1, path2, path3, path4, path5

def _makeSwapFonts(rootPath):
    """ Make some test fonts that have the kerning problem."""
    path1 = os.path.join(rootPath, "Swap.ufo")
    path2 = os.path.join(rootPath, "Swapped.ufo")
    f1 = Font()
    fillInfo(f1)
    addGlyphs(f1, 100)
    f1.features.text = u"# features text from master 1"
    f1.info.ascender = 800
    f1.info.descender = -200
    f1.kerning[('glyphOne', 'glyphOne')] = -10
    f1.kerning[('glyphTwo', 'glyphTwo')] = 10
    f1.save(path1, 2)
    return path1, path2

class DesignSpaceProcessor_using_defcon(DesignSpaceProcessor):
    def _instantiateFont(self, path):
        return defcon.objects.font.Font(path)

class DesignSpaceProcessor_using_fontparts(DesignSpaceProcessor):
    def _instantiateFont(self, path):
        return fontParts.fontshell.font.RFont(path)

def _makeTestDocument(docPath, useVarlib=True, useDefcon=True):
    # make the test fonts and a test document
    if useVarlib:
        extension = "varlib"
    else:
        extension = "mutator"
    testFontPath = os.path.join(os.path.dirname(docPath), "automatic_testfonts_%s" % extension)
    print("\ttestFontPath:", testFontPath)
    m1, m2, i1, anisotropicInstancePath1, anisotropicInstancePath2 = _makeTestFonts(testFontPath)
    if useDefcon:
        d = DesignSpaceProcessor_using_defcon(useVarlib=useVarlib)
    else:
        d = DesignSpaceProcessor_using_fontparts(useVarlib=useVarlib)
    print("\td", d, type(d))
    a = AxisDescriptor()
    a.name = "pop"
    a.minimum = 0
    a.maximum = 1000
    a.default = 0
    a.tag = "pop*"
    a.map = [(500,250)]
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
    s2.muteKerning = True
    d.addSource(s2)

    s3 = SourceDescriptor()
    s3.path = m2
    s3.location = dict(pop=500)
    s3.name = "test.master.support.1"
    s3.layerName = "support"
    d.addSource(s3)

    s4 = SourceDescriptor()
    s4.path = "missing.ufo"
    s4.location = dict(pop=600)
    s4.name = "test.missing.master"
    d.addSource(s4)

    s5 = SourceDescriptor()
    s5.path = m2
    s5.location = dict(pop=620)
    s5.name = "test.existing.ufo_missing.layer"
    s5.layerName = "missing.layer"
    d.addSource(s5)

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
    d.lib['ufoprocessor.testdata'] = dict(pop=500, name="This is a named location, stored in the document lib.")

    d.write(docPath)

def _testGenerateInstances(docPath, useVarlib=True, useDefcon=True):
    # execute the test document
    if useDefcon:
        d = DesignSpaceProcessor_using_defcon(useVarlib=useVarlib)
    else:
        d = DesignSpaceProcessor_using_fontparts(useVarlib=useVarlib)
    d.read(docPath)
    d.loadFonts()
    objectFlavor = [type(f).__name__ for f in d.fonts.values()][0]
    print("objectFlavor", objectFlavor)
    d.generateUFO()
    if d.problems:
        print("log:")
        for p in d.problems:
            print("\t",p)

def testSwap(docPath):
    srcPath, dstPath = _makeSwapFonts(os.path.dirname(docPath))
    f = Font(srcPath)
    swapGlyphNames(f, "narrow", "wide")
    f.info.styleName = "Swapped"
    f.save(dstPath)
    # test the results in newly opened fonts
    old = Font(srcPath)
    new = Font(dstPath)
    assert new.kerning.get(("narrow", "narrow")) == old.kerning.get(("wide","wide"))
    assert new.kerning.get(("wide", "wide")) == old.kerning.get(("narrow","narrow"))
    # after the swap these widths should be the same
    assert old['narrow'].width == new['wide'].width
    assert old['wide'].width == new['narrow'].width
    # The following test may be a bit counterintuitive:
    # the rule swaps the glyphs, but we do not want glyphs that are not
    # specifically affected by the rule to *appear* any different.
    # So, components have to be remapped. 
    assert new['wide.component'].components[0].baseGlyph == "narrow"
    assert new['narrow.component'].components[0].baseGlyph == "wide"

def testAxisMuting():
    d = DesignSpaceProcessor_using_defcon(useVarlib=True)

    a = AxisDescriptor()
    a.name = "pop"
    a.minimum = 0
    a.maximum = 1000
    a.default = 0
    a.tag = "pop*"
    d.addAxis(a)

    a = AxisDescriptor()
    a.name = "snap"
    a.minimum = 100
    a.maximum = 200
    a.default = 150
    a.tag = "snap"
    d.addAxis(a)

    a = AxisDescriptor()
    a.name = "crackle"
    a.minimum = -1
    a.maximum = 1
    a.default = 0
    a.tag = "krak"
    d.addAxis(a)

    shouldIgnore, loc = d.filterThisLocation(dict(snap=150, crackle=0, pop=0), [])
    assert shouldIgnore == False
    assert loc == {'snap': 150, 'crackle': 0, 'pop': 0}

    shouldIgnore, loc = d.filterThisLocation(dict(snap=150, crackle=0, pop=0), ['pop'])
    assert shouldIgnore == False
    assert loc == {'snap': 150, 'crackle': 0}

    shouldIgnore, loc = d.filterThisLocation(dict(snap=150, crackle=0, pop=1), ['pop'])
    assert shouldIgnore == True
    assert loc == {'snap': 150, 'crackle': 0}

    shouldIgnore, loc = d.filterThisLocation(dict(snap=150, crackle=0, pop=0), ['pop', 'crackle'])
    assert shouldIgnore == False
    assert loc == {'snap': 150}

    shouldIgnore, loc = d.filterThisLocation(dict(snap=150, crackle=0, pop=1), ['pop', 'crackle', 'snap'])
    assert shouldIgnore == True
    assert loc == {}

    shouldIgnore, loc = d.filterThisLocation(dict(snap=150, crackle=0, pop=0), ['one', 'two', 'three'])
    assert shouldIgnore == False
    assert loc == {'snap': 150, 'crackle': 0, 'pop': 0}

    shouldIgnore, loc = d.filterThisLocation(dict(snap=150, crackle=0, pop=1), ['one', 'two', 'three'])
    assert shouldIgnore == False
    assert loc == {'snap': 150, 'crackle': 0, 'pop': 1}
    
def testUnicodes(docPath, useVarlib=True):
    # after executing testSwap there should be some test fonts
    # let's check if the unicode values for glyph "narrow" arrive at the right place.
    d = DesignSpaceProcessor(useVarlib=useVarlib)
    d.read(docPath)
    for instance in d.instances:
        if os.path.exists(instance.path):
            f = Font(instance.path)
            print("instance.path", instance.path)
            print("instance.name", instance.name, "f['narrow'].unicodes", f['narrow'].unicodes)
            if instance.name == "TestFamily-TestStyle_pop1000.000":
                assert f['narrow'].unicodes == [291, 292, 293]
            else:
                assert f['narrow'].unicodes == [207]
        else:
            print("Missing test font at %s" % instance.path)

selfTest = True
if selfTest:
    for extension in ['mutator', 'varlib']:
        for objectFlavor in ['defcon', 'fontparts']:
            # which object model to use for **executuing** the designspace.
            # all the objects in **this test** are defcon. 

            print("\n\nRunning the test with ", extension, "and", objectFlavor)
            print("-"*40)
            USEVARLIBMODEL = extension == 'varlib'
            testRoot = os.path.join(os.getcwd(), "automatic_testfonts_%s_%s" % (extension, objectFlavor))
            print("\ttestRoot", testRoot)
            if os.path.exists(testRoot):
                shutil.rmtree(testRoot)
            docPath = os.path.join(testRoot, "automatic_test.designspace")
            print("\tdocPath", docPath)
            print("-"*40)
            print("Generate document, masters")
            _makeTestDocument(docPath, useVarlib=USEVARLIBMODEL, useDefcon=objectFlavor=="defcon")
            print("-"*40)
            print("Generate instances")
            _testGenerateInstances(docPath, useVarlib=USEVARLIBMODEL, useDefcon=objectFlavor=="defcon")
            testSwap(docPath)
            #_makeTestDocument(docPath, useVarlib=USEVARLIBMODEL, useDefcon=objectFlavor=="defcon")
            #_testGenerateInstances(docPath, useVarlib=USEVARLIBMODEL, useDefcon=objectFlavor=="defcon")


testAxisMuting()
