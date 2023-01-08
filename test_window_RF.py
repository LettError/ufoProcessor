""" Test for RF

    what do we want to test?
    + get an idea of how the caching in going
    + get an idea of the speed
    + drawing different types of data, markers, lines, etc
    
     
"""

import vanilla
import importlib
import ufoProcessor.ufoOperator
importlib.reload(ufoProcessor.ufoOperator)
import random

class UFOOperatorTester(object):
    def __init__(self, designspacePath):
        
        self.doc = None
        self.w = vanilla.Window((800,700), "UFOOperator Tester")
        self.w.reloadButton = vanilla.Button((10, 10, 200, 20), "Reload Designspace", callback=self.reloadDesignspace)
        
        self.w.makeSomeInstancesButton = vanilla.Button((10, 40, 400, 20), "Make instances of the same glyph", callback=self.makeInstancesOfSameGlyphButtonCallback)
        self.w.makeSomeGlyphsButton = vanilla.Button((10, 70, 400, 20), "Make instances of different glyphs", callback=self.makeInstancesOfDifferentGlyphsButtonCallback)
        self.w.generateInstancesButton = vanilla.Button((10, 100, 400, 20), "Generate instances", callback=self.generateInstancesButtonCallback)
        self.w.reportGlyphChangedButton = vanilla.Button((10, 130, 400, 20), "Report random glyph as changed", callback=self.reportRandomGlyphChangedButtonCallback)

        self.w.pathText = vanilla.TextBox((230, 12, -10, 20), "...")
        self.w.cacheItemsList = vanilla.List((0, 170, -0, 210),
                     [{"funcName": "A", "count": "a"}, {"funcName": "B", "count": "b"}],
                     columnDescriptions=[{"title": "Function", "key": "funcName"}, {"title": "Items stored", "key": "count"}],
                     selectionCallback=self.selectionCallback)
        self.w.callsToCacheList = vanilla.List((0, 400, -0, -0),
                     [{"funcName": "A", "count": "a"}, {"funcName": "B", "count": "b"}],
                     columnDescriptions=[{"title": "Function", "key": "funcName"}, {"title": "Calls served from cache", "key": "count"}],
                     selectionCallback=self.selectionCallback)
        self.w.open()
        self.w.bind("close", self.closeWindow)
        self.reload()
    
    def reloadDesignspace(self, sender=None):
        print('reloadDesignspace', sender)
        self.reload()
        
    def selectionCallback(self, sender):
        pass

    def closeWindow(self, something=None):
        #print("closeWindow", something)
        self.doc.changed()
        pass
    
    def reportRandomGlyphChangedButtonCallback(self, sender):
        for i in range(10):
            namesLeft = self.doc.glyphsInCache()
            candidateName = None
            if namesLeft:
                candidateName = random.choice(namesLeft)
                print(f'reportRandomGlyphChangedButtonCallback {i} {candidateName}')
            if candidateName:
                self.doc.glyphChanged(candidateName, includeDependencies=True)
        self.updateList()
        
    def generateInstancesButtonCallback(self, sender):
        self.doc.loadFonts()
        self.doc.generateUFOs()
        self.updateList()
        
    def makeInstancesOfSameGlyphButtonCallback(self, sender):
        # make some instances of the same glyph
        hits = 100
        glyphName = random.choice(self.doc.glyphNames)
        for item in range(hits):
            location = self.doc.randomLocation()
            self.doc.makeOneGlyph(glyphName, location, bend=False, decomposeComponents=True, useVarlib=False, roundGeometry=False, clip=False)
        self.updateList()
    
    def makeInstancesOfDifferentGlyphsButtonCallback(self, sender):
        location = self.doc.randomLocation()
        for glyphName in self.doc.glyphNames:
            self.doc.makeOneGlyph(glyphName, location, bend=False, decomposeComponents=True, useVarlib=False, roundGeometry=False, clip=False)
        self.updateList()
                  
    def reload(self):
        if self.doc is not None:
            # we might still have a previous UFOOperator and we need it to clear the cache
            self.doc.changed()
        self.doc = ufoProcessor.ufoOperator.UFOOperator(designspacePath)
        self.doc.loadFonts()
        self.doc.changed()
        self.updateList()

    def updateList(self):
        self.w.pathText.set(designspacePath)
        frequencyItems = []
        objectItems = []
        objects, frequency = ufoProcessor.ufoOperator.inspectMemoizeCache()
        for funcName, count in frequency:
            frequencyItems.append(dict(count=count, funcName= funcName))
        for funcName, count in objects:
            objectItems.append(dict(count=count, funcName= funcName))
        self.w.callsToCacheList.set(frequencyItems)  
        self.w.cacheItemsList.set(objectItems)
        
designspacePath = "/Users/erik/code/ufoProcessor/Tests/ds5/ds5.designspace"
designspacePath = "/Users/erik/code/type2/Principia/sources/Principia_wght_wght.designspace"
UFOOperatorTester(designspacePath)

