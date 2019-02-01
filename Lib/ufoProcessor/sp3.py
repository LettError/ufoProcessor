import os
from fontTools.misc.loggingTools import LogMixin
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, RuleDescriptor, InstanceDescriptor

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# Reader that parses Superpolator documents and buidls designspace objects.
# Note: the Superpolator document format precedes the designspace documnt format.
# For now I just want to migrate data out of Superpolator into designspace.
# So not all data will migrate, just the stuff we can use. 


superpolatorDataLibKey = "com.superpolator.data"    # lib key for Sp data in .designspace

class SuperpolatorReader(LogMixin):
    ruleDescriptorClass = RuleDescriptor
    axisDescriptorClass = AxisDescriptor
    sourceDescriptorClass = SourceDescriptor
    instanceDescriptorClass = InstanceDescriptor

    def __init__(self, documentPath, documentObject):
        self.path = documentPath
        self.documentObject = documentObject
        tree = ET.parse(self.path)
        self.root = tree.getroot()
        self.documentObject.formatVersion = self.root.attrib.get("format", "3.0")
        self.axisDefaults = {}
        self._strictAxisNames = True

    @classmethod
    def fromstring(cls, string, documentObject):
        f = BytesIO(tobytes(string, encoding="utf-8"))
        self = cls(f, documentObject)
        self.path = None
        return self

    def read(self):
        self.readAxes()
        self.readData()
        self.readRules()
        self.readSources()
        self.readInstances()

    def readData(self):
        # read superpolator specific data, view prefs etc.
        dataElements = self.root.findall(".data")
        if not dataElements:
            return

        newLib = {}
        for dataElement in dataElements:
            name = dataElement.attrib.get('name')
            value = dataElement.attrib.get('value')
            if value in ['True', 'False']:
                value = value == "True"
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
            newLib[name] = value
        if newLib:
            self.documentObject.lib[superpolatorDataLibKey] = newLib

    def readRules(self):
        # read the simple rule elements
        rulesContainerElements = self.root.findall(".simplerules")
        print('rulesContainerElements', rulesContainerElements)
        rules = []
        for rulesContainerElement in rulesContainerElements:
            for ruleElement in rulesContainerElement:
                ruleObject = self.ruleDescriptorClass()
                ruleName = ruleObject.name = ruleElement.attrib['name']
                print('rule', ruleName)
                # subs
                for subElement in ruleElement.findall('.sub'):
                    a = subElement.attrib['name']
                    b = subElement.attrib['with']
                    ruleObject.subs.append((a, b))
                # condition sets, .sp3 had none
                externalConditions = self._readConditionElements(
                    ruleElement,
                    ruleName,
                )
                print("externalConditions", externalConditions)
                if externalConditions:
                    ruleObject.conditionSets.append(externalConditions)
                    self.log.info(
                        "Found stray rule conditions outside a conditionset. "
                        "Wrapped them in a new conditionset."
                    )
            print("ruleObject.name", ruleObject.name)
            rules.append(ruleObject)
        self.documentObject.rules = rules

    def _readConditionElements(self, parentElement, ruleName=None):
        # modified from the method from fonttools.designspaceLib
        # it's not the same!
        cds = []
        for conditionElement in parentElement.findall('.condition'):
            cd = {}
            cdMin = conditionElement.attrib.get("minimum")
            if cdMin is not None:
                cd['minimum'] = float(cdMin)
            else:
                # will allow these to be None, assume axis.minimum
                cd['minimum'] = None
            cdMax = conditionElement.attrib.get("maximum")
            if cdMax is not None:
                cd['maximum'] = float(cdMax)
            else:
                # will allow these to be None, assume axis.maximum
                cd['maximum'] = None
            cd['name'] = conditionElement.attrib.get("axisname")
            # # test for things
            if cd.get('minimum') is None and cd.get('maximum') is None:
                raise DesignSpaceDocumentError(
                    "condition missing required minimum or maximum in rule" +
                    (" '%s'" % ruleName if ruleName is not None else ""))
            cds.append(cd)
        return cds

    def readAxes(self):
        # read the axes elements, including the warp map.
        axisElements = self.root.findall(".axis")
        if not axisElements:
            # raise error, we need axes
            print("nope")
            return
        for axisElement in axisElements:
            axisObject = self.axisDescriptorClass()
            axisObject.name = axisElement.attrib.get("name")
            axisObject.tag = axisElement.attrib.get("shortname")
            axisObject.minimum = float(axisElement.attrib.get("minimum"))
            axisObject.maximum = float(axisElement.attrib.get("maximum"))
            axisObject.default = float(axisElement.attrib.get("initialvalue", axisObject.minimum))
            self.documentObject.axes.append(axisObject)
            self.axisDefaults[axisObject.name] = axisObject.default
        self.documentObject.defaultLoc = self.axisDefaults

    def colorFromElement(self, element):
        elementColor = None
        for colorElement in element.findall('.color'):
            elementColor = self.readColorElement(colorElement)

    def readColorElement(self, colorElement):
        print("colorElement", colorElement)
        pass

    def locationFromElement(self, element):
        elementLocation = None
        for locationElement in element.findall('.location'):
            elementLocation = self.readLocationElement(locationElement)
            break
        return elementLocation

    def readLocationElement(self, locationElement):
        """ Format 0 location reader """
        if self._strictAxisNames and not self.documentObject.axes:
            raise DesignSpaceDocumentError("No axes defined")
        loc = {}
        for dimensionElement in locationElement.findall(".dimension"):
            dimName = dimensionElement.attrib.get("name")
            if self._strictAxisNames and dimName not in self.axisDefaults:
                # In case the document contains no axis definitions,
                self.log.warning("Location with undefined axis: \"%s\".", dimName)
                continue
            xValue = yValue = None
            try:
                xValue = dimensionElement.attrib.get('xvalue')
                xValue = float(xValue)
            except ValueError:
                self.log.warning("KeyError in readLocation xValue %3.3f", xValue)
            try:
                yValue = dimensionElement.attrib.get('yvalue')
                if yValue is not None:
                    yValue = float(yValue)
            except ValueError:
                pass
            if yValue is not None:
                loc[dimName] = (xValue, yValue)
            else:
                loc[dimName] = xValue
        return loc

    def readSources(self):
        for sourceCount, sourceElement in enumerate(self.root.findall(".master")):
            filename = sourceElement.attrib.get('filename')
            if filename is not None and self.path is not None:
                sourcePath = os.path.abspath(os.path.join(os.path.dirname(self.path), filename))
            else:
                sourcePath = None
            sourceName = sourceElement.attrib.get('name')
            if sourceName is None:
                # add a temporary source name
                sourceName = "temp_master.%d" % (sourceCount)
            sourceObject = self.sourceDescriptorClass()
            sourceObject.path = sourcePath        # absolute path to the ufo source
            sourceObject.filename = filename      # path as it is stored in the document
            sourceObject.name = sourceName
            familyName = sourceElement.attrib.get("familyname")
            if familyName is not None:
                sourceObject.familyName = familyName
            styleName = sourceElement.attrib.get("stylename")
            if styleName is not None:
                sourceObject.styleName = styleName
            sourceObject.location = self.locationFromElement(sourceElement)
            for libElement in sourceElement.findall('.provideLib'):
                if libElement.attrib.get('state') == '1':
                    sourceObject.copyLib = True
            for groupsElement in sourceElement.findall('.provideGroups'):
                if groupsElement.attrib.get('state') == '1':
                    sourceObject.copyGroups = True
            for infoElement in sourceElement.findall(".provideInfo"):
                if infoElement.attrib.get('state') == '1':
                    sourceObject.copyInfo = True
            for featuresElement in sourceElement.findall(".provideFeatures"):
                if featuresElement.attrib.get('state') == '1':
                    sourceObject.copyFeatures = True
            for glyphElement in sourceElement.findall(".glyph"):
                glyphName = glyphElement.attrib.get('name')
                if glyphName is None:
                    continue
                if glyphElement.attrib.get('mute') == '1':
                    sourceObject.mutedGlyphNames.append(glyphName)
            self.documentObject.sources.append(sourceObject)

    def readInstances(self):
        for instanceCount, instanceElement in enumerate(self.root.findall(".instance")):
            instanceObject = self.instanceDescriptorClass()
            if instanceElement.attrib.get("familyname"):
                instanceObject.familyName = instanceElement.attrib.get("familyname")
            if instanceElement.attrib.get("stylename"):
                instanceObject.styleName = instanceElement.attrib.get("stylename")
            if instanceElement.attrib.get("styleMapFamilyName"):
                instanceObject.styleMapFamilyName = instanceElement.attrib.get("styleMapFamilyName")
            if instanceElement.attrib.get("styleMapStyleName"):
                instanceObject.styleMapStyleName = instanceElement.attrib.get("styleMapStyleName")
            if instanceElement.attrib.get("styleMapFamilyName"):
                instanceObject.styleMapFamilyName = instanceElement.attrib.get("styleMapFamilyName")
            instanceObject.location = self.locationFromElement(instanceElement)
            instanceObject.filename = instanceElement.attrib.get('filename')
            for libElement in instanceElement.findall('.provideLib'):
                if libElement.attrib.get('state') == '1':
                    instanceObject.lib = True
            for libElement in instanceElement.findall('.provideInfo'):
                if libElement.attrib.get('state') == '1':
                    instanceObject.info = True
            self.documentObject.instances.append(instanceObject)

if __name__ == "__main__":
    testDoc = DesignSpaceDocument()
    testPath = "../../Tests/spReader_testdocs/superpolator_testdoc1.sp3"
    reader = SuperpolatorReader(testPath, testDoc)
    reader.read()

    # check the axes
    names = [a.name for a in reader.documentObject.axes]
    names.sort()
    assert names == ['grade', 'space', 'weight', 'width']
    tags = [a.tag for a in reader.documentObject.axes]
    tags.sort()
    assert tags == ['SPCE', 'grad', 'wdth', 'wght']

    # check the data items
    assert superpolatorDataLibKey in reader.documentObject.lib
    items = list(reader.documentObject.lib[superpolatorDataLibKey].items())
    items.sort()
    assert items == [('expandRules', False), ('horizontalPreviewAxis', 'width'), ('includeLegacyRules', False), ('instancefolder', 'instances'), ('keepWorkFiles', True), ('lineInverted', True), ('lineStacked', 'lined'), ('lineViewFilled', True), ('outputFormatUFO', 3.0), ('previewtext', 'VA'), ('roundGeometry', False), ('verticalPreviewAxis', 'weight')]

    # check the sources
    print("reader.documentObject.sources: %d items" % len(reader.documentObject.sources))
    for sd in reader.documentObject.sources:
        assert sd.familyName == "MutatorMathTest_SourceFamilyName"
        if sd.styleName == "Default":
            assert sd.location == {'width': 0.0, 'weight': 0.0, 'space': 0.0, 'grade': -0.5}
            assert sd.copyLib == True
            assert sd.copyGroups == True
            assert sd.copyInfo == True
            assert sd.copyFeatures == True
        elif sd.styleName == "TheOther":
            assert sd.location == {'width': 0.0, 'weight': 1000.0, 'space': 0.0, 'grade': -0.5}
            assert sd.copyLib == False
            assert sd.copyGroups == False
            assert sd.copyInfo == False
            assert sd.copyFeatures == False

    # check the instances
    print("reader.documentObject.instances: %d items" % len(reader.documentObject.instances))
    for nd in reader.documentObject.instances:
        assert nd.familyName == "MutatorMathTest_InstanceFamilyName"
        if nd.styleName == "AWeightThatILike":
            assert nd.location == {'width': 133.152174, 'weight': 723.981097, 'space': 0.0, 'grade': -0.5}
            assert nd.filename == "instances/MutatorMathTest_InstanceFamilyName-AWeightThatILike.ufo"
            assert nd.styleMapFamilyName == None
            assert nd.styleMapStyleName == None
        if nd.styleName == "wdth759.79_SPCE0.00_wght260.72":
            # note the anisotropic location in the width axis.
            assert nd.location == {'width': (500.0, 800.0), 'weight': 260.7217, 'space': 0.0, 'grade': -0.5}
            assert nd.filename == "instances/MutatorMathTest_InstanceFamilyName-wdth759.79_SPCE0.00_wght260.72.ufo"
            assert nd.styleMapFamilyName == "StyleMappedFamily"
            assert nd.styleMapStyleName == "bold"

    # check the rules
    for rd in reader.documentObject.rules:
        assert rd.name == "width: < 500.0"
        assert len(rd.conditionSets) == 1
        assert rd.subs == [('I', 'I.narrow')]
        for conditionSet in rd.conditionSets:
            for cd in conditionSet:
                print(cd)
                if cd['name'] == "width":
                    assert cd == {'minimum': None, 'maximum': 500.0, 'name': 'width'}
                if cd['name'] == "grade":
                    assert cd == {'minimum': 0.0, 'maximum': 500.0, 'name': 'grade'}


    testDoc.write(testPath.replace(".sp3", "_output_roundtripped.designspace"))

