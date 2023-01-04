import os
import glob
import functools


import defcon
from warnings import warn
import collections
import logging, traceback

from ufoProcessor import DesignSpaceProcessor
from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, InstanceDescriptor, AxisDescriptor, RuleDescriptor, processRules
from fontTools.designspaceLib.split import splitInterpolable
from fontTools.ufoLib import fontInfoAttributesVersion1, fontInfoAttributesVersion2, fontInfoAttributesVersion3

from fontTools.misc import plistlib
from fontMath.mathGlyph import MathGlyph
from fontMath.mathInfo import MathInfo
from fontMath.mathKerning import MathKerning
from mutatorMath.objects.mutator import buildMutator
from mutatorMath.objects.location import Location

import ufoProcessor.varModels
from ufoProcessor.varModels import VariationModelMutator
from ufoProcessor.emptyPen import checkGlyphIsEmpty

from ufoProcessor.logger import Logger

_memoizeCache = dict()

def immutify(obj):
    # make an immutable version of this object. 
    # assert immutify(10) == (10,)
    # assert immutify([10, 20, "a"]) == (10, 20, 'a')
    # assert immutify(dict(foo="bar", world=["a", "b"])) == ('foo', ('bar',), 'world', ('a', 'b'))
    hashValues = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            hashValues.extend([key, immutify(value)])
    elif isinstance(obj, list):
        for value in obj:
            hashValues.extend(immutify(value))
    else:
        hashValues.append(obj)
    return tuple(hashValues)


def memoize(function):
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):        
        immutableargs = tuple([immutify(a) for a in args])
        immutablekwargs = immutify(kwargs)
        key = (function.__name__, self, immutableargs, immutify(kwargs))
        if key in _memoizeCache:
            return _memoizeCache[key]
        else:
            result = function(self, *args, **kwargs)
            _memoizeCache[key] = result
            return result
    return wrapper


def getUFOVersion(ufoPath):
    # Peek into a ufo to read its format version.
            # <?xml version="1.0" encoding="UTF-8"?>
            # <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            # <plist version="1.0">
            # <dict>
            #   <key>creator</key>
            #   <string>org.robofab.ufoLib</string>
            #   <key>formatVersion</key>
            #   <integer>2</integer>
            # </dict>
            # </plist>
    metaInfoPath = os.path.join(ufoPath, "metainfo.plist")
    with open(metaInfoPath, 'rb') as f:
        p = plistlib.load(f)
        return p.get('formatVersion')

def getDefaultLayerName(f):
    # get the name of the default layer from a defcon font and from a fontparts font
    if issubclass(type(f), defcon.objects.font.Font):
        return f.layers.defaultLayer.name
    elif issubclass(type(f), fontParts.fontshell.font.RFont):
        return f.defaultLayer.name
    return None

# wrapped, not inherited
class NewUFOProcessor(object):
    
    fontClass = defcon.Font
    layerClass = defcon.Layer
    glyphClass = defcon.Glyph
    libClass = defcon.Lib
    glyphContourClass = defcon.Contour
    glyphPointClass = defcon.Point
    glyphComponentClass = defcon.Component
    glyphAnchorClass = defcon.Anchor
    kerningClass = defcon.Kerning
    groupsClass = defcon.Groups
    infoClass = defcon.Info
    featuresClass = defcon.Features

    mathInfoClass = MathInfo
    mathGlyphClass = MathGlyph
    mathKerningClass = MathKerning

    def __init__(self, pathOrObject=None, ufoVersion=3, useVarlib=True, debug =False):
        self.ufoVersion = ufoVersion
        self.useVarlib = useVarlib
        self._fontsLoaded = False
        self.problems = []
        self.fonts = {}
        self.roundGeometry = False
        self.mutedAxisNames = None    # list of axisname that need to be muted
        self.debug = debug
        self.logger = None
    
        if isinstance(pathOrObject, str):
            self.doc = DesignSpaceDocument()
            self.doc.read(pathOrObject)
        else:
            # XX test this
            self.doc = pathOrObject

        if self.debug:
            docBaseName = os.path.splitext(self.doc.path)[0]
            logPath = f"{docBaseName}_log.txt"
            self.logger = Logger(path=logPath, rootDirectory=None)
            self.logger.time()
            self.logger.info(f"## {self.doc.path}")
            self.logger.info(f"\tUFO version: {self.ufoVersion}")
            self.logger.info(f"\tround Geometry: {self.roundGeometry}")
            if self.useVarlib:
                self.logger.info(f"\tinterpolating with varlib")
            else:
                self.logger.info(f"\tinterpolating with mutatorMath")

    def _instantiateFont(self, path):
        """ Return a instance of a font object with all the given subclasses"""
        try:
            return self.fontClass(path,
                layerClass=self.layerClass,
                libClass=self.libClass,
                kerningClass=self.kerningClass,
                groupsClass=self.groupsClass,
                infoClass=self.infoClass,
                featuresClass=self.featuresClass,
                glyphClass=self.glyphClass,
                glyphContourClass=self.glyphContourClass,
                glyphPointClass=self.glyphPointClass,
                glyphComponentClass=self.glyphComponentClass,
                glyphAnchorClass=self.glyphAnchorClass)
        except TypeError:
            # if our fontClass doesnt support all the additional classes
            return self.fontClass(path)

    def loadFonts(self, reload=False):
        # Load the fonts and find the default candidate based on the info flag
        if self._fontsLoaded and not reload:
            return
        names = set()
        actions = []
        if self.debug:
            self.logger.info("## loadFonts")
        for i, sourceDescriptor in enumerate(self.doc.sources):
            if sourceDescriptor.name is None:
                # make sure it has a unique name
                sourceDescriptor.name = "source.%d" % i
            if sourceDescriptor.name not in self.fonts:
                #
                if os.path.exists(sourceDescriptor.path):
                    self.fonts[sourceDescriptor.name] = self._instantiateFont(sourceDescriptor.path)
                    thisLayerName = getDefaultLayerName(self.fonts[sourceDescriptor.name])
                    actions.append(f"loaded: {os.path.basename(sourceDescriptor.path)}, layer: {thisLayerName}, format: {getUFOVersion(sourceDescriptor.path)}")
                    names |= set(self.fonts[sourceDescriptor.name].keys())
                else:
                    self.fonts[sourceDescriptor.name] = None
                    actions.append("source ufo not found at %s" % (sourceDescriptor.path))
        self.glyphNames = list(names)
        if self.debug:
            for item in actions:
                self.logger.infoItem(item)

        self._fontsLoaded = True
   
    def splitLocation(self, location):
        # split a location in a continouous and a discrete part
        discreteAxes = [a.name for a in self.getOrderedDiscreteAxes()]
        continuous = {}
        discrete = {}
        for name, value in location.items():
            if name in discreteAxes:
                discrete[name] = value
            else:
                continuous[name] = value
        if not discrete:
            return continuous, None
        return continuous, discrete

    def _serializeAnyAxis(self, axis):
        if hasattr(axis, "serialize"):
            return axis.serialize()
        else:
            if hasattr(axis, "values"):
                # discrete axis does not have serialize method, meh
                return dict(
                    tag=axis.tag,
                    name=axis.name,
                    labelNames=axis.labelNames,
                    minimum = min(axis.values), # XX is this allowed
                    maximum = max(axis.values), # XX is this allowed
                    values=axis.values,
                    default=axis.default,
                    hidden=axis.hidden,
                    map=axis.map,
                    axisOrdering=axis.axisOrdering,
                    axisLabels=axis.axisLabels,
                )

    def getSerializedAxes(self, discreteLocation=None):
        serialized = []
        for axis in self.getOrderedContinuousAxes():
            serialized.append(self._serializeAnyAxis(axis))
        return serialized

    def getContinuousAxesForMutator(self):
        # map the axis values?
        d = collections.OrderedDict()
        for axis in self.getOrderedContinuousAxes():
            d[axis.name] = self._serializeAnyAxis(axis)
        return d

    def _getAxisOrder(self):
        return [a.name for a in self.doc.axes]

    axisOrder = property(_getAxisOrder, doc="get the axis order from the axis descriptors")

    #serializedAxes = property(getSerializedAxes, doc="a list of dicts with the axis values")

    # some ds5 work
    def getOrderedDiscreteAxes(self):
        # return the list of discrete axis objects, in the right order
        axes = []
        for axisName in self.doc.getAxisOrder():
            axisObj = self.doc.getAxis(axisName)
            if hasattr(axisObj, "values"):
                axes.append(axisObj)
        return axes

    def getOrderedContinuousAxes(self):
        # return the list of continuous axis objects, in the right order
        axes = []
        for axisName in self.doc.getAxisOrder():
            axisObj = self.doc.getAxis(axisName)
            if not hasattr(axisObj, "values"):
                axes.append(axisObj)
        return axes

    @memoize
    def findSourceDescriptorsForDiscreteLocation(self, discreteLocDict):
        # return a list of all sourcedescriptors that share the values in the discrete loc tuple
        # so this includes all sourcedescriptors that point to layers
        # discreteLocDict {'countedItems': 1.0, 'outlined': 0.0}, {'countedItems': 1.0, 'outlined': 1.0}
        sources = []
        for s in self.doc.sources:
            ok = True
            if discreteLocDict is None:
                sources.append(s)
                continue
            for name, value in discreteLocDict.items():
                if name in s.location:
                    if s.location[name] != value:
                        ok = False
                else:
                    ok = False
                    continue
            if ok:
                sources.append(s)
        return sources

    def getVariationModel(self, items, axes, bias=None):
        # Return either a mutatorMath or a varlib.model object for calculating.
        #try:
        if True:
            if self.useVarlib:
                # use the varlib variation model
                try:
                    return dict(), VariationModelMutator(items, axes=self.doc.axes, extrapolate=True)
                    #return dict(), VariationModelMutator(items, axes=self.doc.axes)
                except TypeError:
                    import fontTools.varLib.models
                    error = traceback.format_exc()
                    note = "Error while making VariationModelMutator for {loc}:\n{error}"
                    if self.debug:
                        self.logger.info(note)
                    return {}, None
                except (KeyError, AssertionError):
                    error = traceback.format_exc()
                    self.toolLog.append("UFOProcessor.getVariationModel error: %s" % error)
                    self.toolLog.append(items)
                    return {}, None
            else:
                # use mutatormath model
                axesForMutator = self.getContinuousAxesForMutator()
                # mutator will be confused by discrete axis values.
                # the bias needs to be for the continuous axes only
                biasForMutator, _ = self.splitLocation(bias)
                return buildMutator(items, axes=axesForMutator, bias=biasForMutator)
        #except:
        #    error = traceback.format_exc()
        #    self.toolLog.append("UFOProcessor.getVariationModel error: %s" % error)
        return {}, None

    @memoize
    def newDefaultLocation(self, bend=False, discreteLocation=None):
        # overwrite from fontTools.newDefaultLocation
        # we do not want this default location always to be mapped.
        loc = collections.OrderedDict()
        for axisDescriptor in self.doc.axes:
            axisName = axisDescriptor.name
            axisValue = axisDescriptor.default
            if discreteLocation is not None:
                # if we want to find the default for a specific discreteLoation
                # we can not use the discrete axis' default value
                # -> we have to use the value in the given discreteLocation
                if axisDescriptor.name in discreteLocation:
                    axisValue = discreteLocation[axisDescriptor.name]
            else:
                axisValue = axisDescriptor.default
            if bend:
                loc[axisName] = axisDescriptor.map_forward(
                    axisValue
                )
            else:
                loc[axisName] = axisValue
        return loc

    @memoize
    def isAnisotropic(self, location):
        for v in location.values():
            if isinstance(v, (list, tuple)):
                return True
        return False

    @memoize
    def splitAnisotropic(self, location):
        x = Location()
        y = Location()
        for dim, val in location.items():
            if type(val)==tuple:
                x[dim] = val[0]
                y[dim] = val[1]
            else:
                x[dim] = y[dim] = val
        return x, y

    @memoize
    def _getAxisOrder(self):
        return [a.name for a in self.doc.axes]
    
    def generateUFOs(self):
        self.loadFonts()
        if self.debug:
            self.logger.info("## generateUFO")
        for loc, space in splitInterpolable(self.doc):
            spaceDoc = self.__class__(pathOrObject=space)
            if self.debug:
                self.logger.infoItem(f"Generating UFOs for continuous space at discrete location {loc}")
            v = 0
            for instanceDescriptor in self.doc.instances:
                if instanceDescriptor.path is None:
                    continue
                pairs = None
                bend = False
                font = self.makeInstance(instanceDescriptor,
                        processRules,
                        glyphNames=self.glyphNames,
                        pairs=pairs,
                        bend=bend,
                        )
                if self.debug:
                    self.logger.info(f"\t\t{os.path.basename(instanceDescriptor.path)}")
                instanceFolder = os.path.dirname(instanceDescriptor.path)
                if not os.path.exists(instanceFolder):
                    os.makedirs(instanceFolder)
                font.save(instanceDescriptor.path)

    generateUFO = generateUFOs

    @memoize
    def getInfoMutator(self, discreteLocation=None):
        """ Returns a info mutator """
        infoItems = []
        if discreteLocation is not None:
            sources = self.findSourceDescriptorsForDiscreteLocation(discreteLocation)
        else:
            sources = self.doc.sources
        for sourceDescriptor in sources:
            if sourceDescriptor.layerName is not None:
                continue
            continuous, discrete = self.splitLocation(sourceDescriptor.location)
            loc = Location(continuous)
            sourceFont = self.fonts[sourceDescriptor.name]
            if sourceFont is None:
                continue
            if hasattr(sourceFont.info, "toMathInfo"):
                infoItems.append((loc, sourceFont.info.toMathInfo()))
            else:
                infoItems.append((loc, self.mathInfoClass(sourceFont.info)))
        infoBias = self.newDefaultLocation(bend=True, discreteLocation=discreteLocation)
        bias, self._infoMutator = self.getVariationModel(infoItems, axes=self.getSerializedAxes(), bias=infoBias)
        return self._infoMutator

    @memoize
    def getKerningMutator(self, pairs=None, discreteLocation=None):
        """ Return a kerning mutator, collect the sources, build mathGlyphs.
            If no pairs are given: calculate the whole table.
            If pairs are given then query the sources for a value and make a mutator only with those values.
        """
        if discreteLocation is not None:
            sources = self.findSourceDescriptorsForDiscreteLocation(discreteLocation)
        else:
            sources = self.sources
        kerningItems = []
        foregroundLayers = [None, 'foreground', 'public.default']
        if pairs is None:
            for sourceDescriptor in sources:
                if sourceDescriptor.layerName not in foregroundLayers:
                    continue
                if not sourceDescriptor.muteKerning:
                    # filter this XX @@
                    continuous, discrete = self.splitLocation(sourceDescriptor.location)
                    loc = Location(continuous)
                    sourceFont = self.fonts[sourceDescriptor.name]
                    if sourceFont is None: continue
                    # this makes assumptions about the groups of all sources being the same.
                    kerningItems.append((loc, self.mathKerningClass(sourceFont.kerning, sourceFont.groups)))
        else:
            self._kerningMutatorPairs = pairs
            for sourceDescriptor in sources:
                # XXX check sourceDescriptor layerName, only foreground should contribute
                if sourceDescriptor.layerName is not None:
                    continue
                if not os.path.exists(sourceDescriptor.path):
                    continue
                if not sourceDescriptor.muteKerning:
                    sourceFont = self.fonts[sourceDescriptor.name]
                    if sourceFont is None:
                        continue
                    continuous, discrete = self.splitLocation(sourceDescriptor.location)
                    loc = Location(continuous)
                    # XXX can we get the kern value from the fontparts kerning object?
                    kerningItem = self.mathKerningClass(sourceFont.kerning, sourceFont.groups)
                    if kerningItem is not None:
                        sparseKerning = {}
                        for pair in pairs:
                            v = kerningItem.get(pair)
                            if v is not None:
                                sparseKerning[pair] = v
                        kerningItems.append((loc, self.mathKerningClass(sparseKerning)))
        kerningBias = self.newDefaultLocation(bend=True, discreteLocation=discreteLocation)
        bias, thing = self.getVariationModel(kerningItems, axes=self.getSerializedAxes(), bias=kerningBias) #xx
        bias, self._kerningMutator = self.getVariationModel(kerningItems, axes=self.getSerializedAxes(), bias=kerningBias)
        return self._kerningMutator

    @memoize
    def getGlyphMutator(self, glyphName,
            decomposeComponents=False,
            **discreteLocation,  
            ):
        fromCache = False
        # make a mutator / varlib object for glyphName, with the sources for the given discrete location
        items, unicodes = self.collectSourcesForGlyph(glyphName, decomposeComponents=decomposeComponents, **discreteLocation)
        new = []
        for a, b, c in items:
            if hasattr(b, "toMathGlyph"):
                # note: calling toMathGlyph ignores the mathGlyphClass preference
                # maybe the self.mathGlyphClass is not necessary?
                new.append((a,b.toMathGlyph()))
            else:
                new.append((a,self.mathGlyphClass(b)))
        thing = None
        thisBias = self.newDefaultLocation(bend=True, discreteLocation=discreteLocation)
        try:
            bias, thing = self.getVariationModel(new, axes=self.getSerializedAxes(), bias=thisBias) #xx
        except:
            error = traceback.format_exc()
            note = f"Error in getGlyphMutator for {glyphName}:\n{error}"
            if self.debug:
                self.logger.info(note)
        return thing, unicodes

    @memoize
    def isLocalDefault(self, location):
        # return True if location is a local default
        defaults = {}
        for aD in self.doc.axes:
            defaults[aD.name] = aD.default
        for axisName, value in location.items():
            if defaults[axisName] != value:
                return False
        return True

    @memoize
    def filterThisLocation(self, location, mutedAxes=None):
        # return location with axes is mutedAxes removed
        # this means checking if the location is a non-default value
        if not mutedAxes:
            return False, location
        defaults = {}
        ignoreSource = False
        for aD in self.doc.axes:
            defaults[aD.name] = aD.default
        new = {}
        new.update(location)
        for mutedAxisName in mutedAxes:
            if mutedAxisName not in location:
                continue
            if mutedAxisName not in defaults:
                continue
            if location[mutedAxisName] != defaults.get(mutedAxisName):
                ignoreSource = True
            del new[mutedAxisName]
        return ignoreSource, new

    @memoize
    def collectSourcesForGlyph(self, glyphName, decomposeComponents=False, discreteLocation=None):
        """ Return a glyph mutator
            decomposeComponents = True causes the source glyphs to be decomposed first
            before building the mutator. That gives you instances that do not depend
            on a complete font. If you're calculating previews for instance.

            findSourceDescriptorsForDiscreteLocation returns sources from layers as well
        """
        items = []
        empties = []
        foundEmpty = False
        # is bend=True necessary here?
        defaultLocation = self.newDefaultLocation(bend=True, discreteLocation=discreteLocation)
        # 
        if discreteLocation is not None:
            sources = self.findSourceDescriptorsForDiscreteLocation(discreteLocation)
        else:
            sources = self.doc.sources
        unicodes = set()       # unicodes for this glyph
        for sourceDescriptor in sources:
            if not os.path.exists(sourceDescriptor.path):
                #kthxbai
                p = "\tMissing UFO at %s" % sourceDescriptor.path
                if p not in self.problems:
                    self.problems.append(p)
                continue
            if glyphName in sourceDescriptor.mutedGlyphNames:
                self.logger.info(f"\t\tglyphName {glyphName} is muted")
                continue
            thisIsDefault = self.isLocalDefault(sourceDescriptor.location)
            ignoreSource, filteredLocation = self.filterThisLocation(sourceDescriptor.location, self.mutedAxisNames)
            if ignoreSource:
                continue
            f = self.fonts.get(sourceDescriptor.name)
            if f is None: continue
            loc = Location(sourceDescriptor.location)
            sourceLayer = f
            if not glyphName in f:
                # log this>
                continue
            layerName = getDefaultLayerName(f)
            sourceGlyphObject = None
            # handle source layers
            if sourceDescriptor.layerName is not None:
                # start looking for a layer
                # Do not bother for mutatorMath designspaces
                layerName = sourceDescriptor.layerName
                sourceLayer = getLayer(f, sourceDescriptor.layerName)
                if sourceLayer is None:
                    continue
                if glyphName not in sourceLayer:
                    # start looking for a glyph
                    # this might be a support in a sparse layer
                    # so we're skipping!
                    continue
            # still have to check if the sourcelayer glyph is empty
            if not glyphName in sourceLayer:
                continue
            else:
                sourceGlyphObject = sourceLayer[glyphName]
                if sourceGlyphObject.unicodes is not None:
                    for u in sourceGlyphObject.unicodes:
                        unicodes.add(u)
                if checkGlyphIsEmpty(sourceGlyphObject, allowWhiteSpace=True):
                    foundEmpty = True
                    #sourceGlyphObject = None
                    #continue
            if decomposeComponents:
                # what about decomposing glyphs in a partial font?
                temp = self.glyphClass()
                p = temp.getPointPen()
                dpp = DecomposePointPen(sourceLayer, p)
                sourceGlyphObject.drawPoints(dpp)
                temp.width = sourceGlyphObject.width
                temp.name = sourceGlyphObject.name
                processThis = temp
            else:
                processThis = sourceGlyphObject
            sourceInfo = dict(source=f.path, glyphName=glyphName,
                    layerName=layerName,
                    location=filteredLocation,  #   sourceDescriptor.location,
                    sourceName=sourceDescriptor.name,
                    )
            if hasattr(processThis, "toMathGlyph"):
                processThis = processThis.toMathGlyph()
            else:
                processThis = self.mathGlyphClass(processThis)
            # this is where the location is linked to the glyph
            # this loc needs to have the discrete location subtracted
            # XX @@
            continuous, discrete = self.splitLocation(loc)
            items.append((continuous, processThis, sourceInfo))
            empties.append((thisIsDefault, foundEmpty))
        # check the empties:
        # if the default glyph is empty, then all must be empty
        # if the default glyph is not empty then none can be empty
        checkedItems = []
        emptiesAllowed = False
        # first check if the default is empty.
        # remember that the sources can be in any order
        for i, p in enumerate(empties):
            isDefault, isEmpty = p
            if isDefault and isEmpty:
                emptiesAllowed = True
                # now we know what to look for
        if not emptiesAllowed:
            for i, p in enumerate(empties):
                isDefault, isEmpty = p
                if not isEmpty:
                    checkedItems.append(items[i])
        else:
            for i, p in enumerate(empties):
                isDefault, isEmpty = p
                if isEmpty:
                    checkedItems.append(items[i])
        return checkedItems, unicodes

    collectMastersForGlyph = collectSourcesForGlyph

    def makeInstance(self, instanceDescriptor,
            doRules=None,
            glyphNames=None,
            pairs=None,
            bend=False):
        """ Generate a font object for this instance """
        if doRules is not None:
            warn('The doRules argument in DesignSpaceProcessor.makeInstance() is deprecated', DeprecationWarning, stacklevel=2)
        continuousLocation, discreteLocation = self.splitLocation(instanceDescriptor.location)

        font = self._instantiateFont(None)

        loc = Location(continuousLocation)
        anisotropic = False
        locHorizontal = locVertical = loc
        if self.isAnisotropic(loc):
            anisotropic = True
            locHorizontal, locVertical = self.splitAnisotropic(loc)
            if self.debug:
                self.logger.info(f"\t\t\tAnisotropic location for {instanceDescriptor.name}\n\t\t\t{instanceDescriptor.location}")
        if instanceDescriptor.kerning:
            if pairs:
                try:
                    kerningMutator = self.getKerningMutator(pairs=pairs, discreteLocation=discreteLocation)
                    kerningObject = kerningMutator.makeInstance(locHorizontal, bend=bend)
                    kerningObject.extractKerning(font)
                except:
                    error = traceback.format_exc()
                    note = f"Could not make kerning for {loc}\n{error}"
                    if self.debug:
                        self.logger.info(note)
            else:
                kerningMutator = self.getKerningMutator(discreteLocation=discreteLocation)
                if kerningMutator is not None:
                    kerningObject = kerningMutator.makeInstance(locHorizontal, bend=bend)
                    kerningObject.extractKerning(font)
                    if self.debug:
                        self.logger.info(f"\t\t\t{len(font.kerning)} kerning pairs added")

        
        # # make the info
        infoMutator = self.getInfoMutator(discreteLocation=discreteLocation)
        if infoMutator is not None:
            if not anisotropic:
                infoInstanceObject = infoMutator.makeInstance(loc, bend=bend)
            else:
                horizontalInfoInstanceObject = infoMutator.makeInstance(locHorizontal, bend=bend)
                verticalInfoInstanceObject = infoMutator.makeInstance(locVertical, bend=bend)
                # merge them again
                infoInstanceObject = (1,0)*horizontalInfoInstanceObject + (0,1)*verticalInfoInstanceObject
            if self.roundGeometry:
                infoInstanceObject = infoInstanceObject.round()
            infoInstanceObject.extractInfo(font.info)
        font.info.familyName = instanceDescriptor.familyName
        font.info.styleName = instanceDescriptor.styleName
        font.info.postscriptFontName = instanceDescriptor.postScriptFontName # yikes, note the differences in capitalisation..
        font.info.styleMapFamilyName = instanceDescriptor.styleMapFamilyName
        font.info.styleMapStyleName = instanceDescriptor.styleMapStyleName
                
        for sourceDescriptor in self.doc.sources:
            if sourceDescriptor.copyInfo:
                # this is the source
                if self.fonts[sourceDescriptor.name] is not None:
                    self._copyFontInfo(self.fonts[sourceDescriptor.name].info, font.info)
            if sourceDescriptor.copyLib:
                # excplicitly copy the font.lib items
                if self.fonts[sourceDescriptor.name] is not None:
                    for key, value in self.fonts[sourceDescriptor.name].lib.items():
                        font.lib[key] = value
            if sourceDescriptor.copyGroups:
                if self.fonts[sourceDescriptor.name] is not None:
                    for key, value in self.fonts[sourceDescriptor.name].groups.items():
                        font.groups[key] = value
            if sourceDescriptor.copyFeatures:
                if self.fonts[sourceDescriptor.name] is not None:
                    featuresText = self.fonts[sourceDescriptor.name].features.text
                    font.features.text = featuresText

        # ok maybe now it is time to calculate some glyphs
        # glyphs
        if glyphNames:
            selectedGlyphNames = glyphNames
        else:
            selectedGlyphNames = self.glyphNames
        if not 'public.glyphOrder' in font.lib.keys():
            # should be the glyphorder from the default, yes?
            font.lib['public.glyphOrder'] = selectedGlyphNames

        for glyphName in selectedGlyphNames:
            glyphMutator, unicodes = self.getGlyphMutator(glyphName, discreteLocation=discreteLocation)
            if glyphMutator is None:
                self.problems.append("Could not make mutator for glyph %s" % (glyphName))
                continue

            font.newGlyph(glyphName)
            font[glyphName].clear()
            glyphInstanceUnicodes = []
            #neutralFont = self.getNeutralFont()
            font[glyphName].unicodes = unicodes

            try:
                if not self.isAnisotropic(continuousLocation):
                    glyphInstanceObject = glyphMutator.makeInstance(continuousLocation, bend=bend)
                else:
                    # split anisotropic location into horizontal and vertical components
                    horizontalGlyphInstanceObject = glyphMutator.makeInstance(locHorizontal, bend=bend)
                    verticalGlyphInstanceObject = glyphMutator.makeInstance(locVertical, bend=bend)
                    # merge them again
                    glyphInstanceObject = (1,0)*horizontalGlyphInstanceObject + (0,1)*verticalGlyphInstanceObject
            except IndexError:
                # alignment problem with the data?
                note = "Quite possibly some sort of data alignment error in %s" % glyphName
                if self.debug:
                    self.logger.info(note)
                self.problems.append(note)
                continue
            if self.roundGeometry:
                try:
                    glyphInstanceObject = glyphInstanceObject.round()
                except AttributeError:
                    # what are we catching here? 
                    print(f"no round method for {glyphInstanceObject} ?")
                    pass
            try:
                # File "/Users/erik/code/ufoProcessor/Lib/ufoProcessor/__init__.py", line 649, in makeInstance
                #   glyphInstanceObject.extractGlyph(font[glyphName], onlyGeometry=True)
                # File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontMath/mathGlyph.py", line 315, in extractGlyph
                #   glyph.anchors = [dict(anchor) for anchor in self.anchors]
                # File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/base.py", line 103, in __set__
                #   raise FontPartsError("no setter for %r" % self.name)
                #   fontParts.base.errors.FontPartsError: no setter for 'anchors'
                if hasattr(font[glyphName], "fromMathGlyph"):
                    font[glyphName].fromMathGlyph(glyphInstanceObject)
                else:
                    glyphInstanceObject.extractGlyph(font[glyphName], onlyGeometry=True)
            except TypeError:
                # this causes ruled glyphs to end up in the wrong glyphname
                # but defcon2 objects don't support it
                pPen = font[glyphName].getPointPen()
                font[glyphName].clear()
                glyphInstanceObject.drawPoints(pPen)
            font[glyphName].width = glyphInstanceObject.width

        if self.debug:
            self.logger.info(f"\t\t\t{len(selectedGlyphNames)} glyphs added")

        return font
    
    def _copyFontInfo(self, sourceInfo, targetInfo):
        """ Copy the non-calculating fields from the source info."""
        infoAttributes = [
            "versionMajor",
            "versionMinor",
            "copyright",
            "trademark",
            "note",
            "openTypeGaspRangeRecords",
            "openTypeHeadCreated",
            "openTypeHeadFlags",
            "openTypeNameDesigner",
            "openTypeNameDesignerURL",
            "openTypeNameManufacturer",
            "openTypeNameManufacturerURL",
            "openTypeNameLicense",
            "openTypeNameLicenseURL",
            "openTypeNameVersion",
            "openTypeNameUniqueID",
            "openTypeNameDescription",
            "#openTypeNamePreferredFamilyName",
            "#openTypeNamePreferredSubfamilyName",
            "#openTypeNameCompatibleFullName",
            "openTypeNameSampleText",
            "openTypeNameWWSFamilyName",
            "openTypeNameWWSSubfamilyName",
            "openTypeNameRecords",
            "openTypeOS2Selection",
            "openTypeOS2VendorID",
            "openTypeOS2Panose",
            "openTypeOS2FamilyClass",
            "openTypeOS2UnicodeRanges",
            "openTypeOS2CodePageRanges",
            "openTypeOS2Type",
            "postscriptIsFixedPitch",
            "postscriptForceBold",
            "postscriptDefaultCharacter",
            "postscriptWindowsCharacterSet"
        ]
        for infoAttribute in infoAttributes:
            copy = False
            if self.ufoVersion == 1 and infoAttribute in fontInfoAttributesVersion1:
                copy = True
            elif self.ufoVersion == 2 and infoAttribute in fontInfoAttributesVersion2:
                copy = True
            elif self.ufoVersion == 3 and infoAttribute in fontInfoAttributesVersion3:
                copy = True
            if copy:
                value = getattr(sourceInfo, infoAttribute)
                setattr(targetInfo, infoAttribute, value)

    # updating fonts
    def updateFonts(self, fontObjects):
        # this is to update the loaded fonts. 
        # it should be the way for an editor to provide a list of fonts that are open
        #self.fonts[sourceDescriptor.name] = None
        hasUpdated = False
        for newFont in fontObjects:
            for fontName, haveFont in self.fonts.items():
                if haveFont.path == newFont.path and id(haveFont)!=id(newFont):
                    note = f"## updating source {self.fonts[fontName]} with {newFont.path}"
                    if self.debug:
                        self.logger.time()
                        self.logger.info(note)
                    self.fonts[fontName] = newFont
                    hasUpdated = True
        if hasUpdated:
            self.changed()


if __name__ == "__main__":

    ds5Path = "/Users/erik/code/type2/Principia/sources/Principia_wdth.designspace"
    #ds5Path = "../../Tests/ds5/ds5.designspace"

    dumpCacheLog = False
    import os
    if os.path.exists(ds5Path):
        doc = NewUFOProcessor(ds5Path, useVarlib=False, debug=True)
        doc.generateUFOs()
        print("sources for space.tight ", doc.collectSourcesForGlyph("space.tight"))

        if dumpCacheLog:
            doc.logger.info(f"Test: cached {len(_memoizeCache)} items")
            for key, item in _memoizeCache.items():
                doc.logger.info(f"\t\t{key} {item}")

