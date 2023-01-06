# make a test designspace format 4 with 1 continuous axis
# shouls save as format 4?

# axis width is a normal interpolation with a change in width

from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, InstanceDescriptor, AxisDescriptor, RuleDescriptor, processRules, DiscreteAxisDescriptor
from fontTools.designspaceLib.split import splitInterpolable

import os
import fontTools
print(fontTools.version)

import ufoProcessor
print(ufoProcessor.__file__)
import ufoProcessor.ufoOperator
#doc = DesignSpaceDocument()

doc = ufoProcessor.ufoOperator.UFOOperator()
doc.formatVersion = "4.0"
print(doc.formatVersion)

#https://fonttools.readthedocs.io/en/latest/designspaceLib/python.html#axisdescriptor
a1 = AxisDescriptor()
a1.minimum = 400
a1.maximum = 1000
a1.default = 400
a1.map = ((400,400), (700,900), (1000,1000))
a1.name = "width"
a1.tag = "wdth"
#a1.axisOrdering = 1 		# if we add this the doc version will go to 5.0
doc.addAxis(a1)

default = {a1.name: a1.default}

# add sources

for c in [a1.minimum, a1.maximum]:
	s1 = SourceDescriptor()
	s1.path = os.path.join("sources", f"geometrySource_c_{c}.ufo")
	s1.name = f"geometrySource{c}"
	sourceLocation = dict(width=c)
	s1.location = sourceLocation
	s1.kerning = True
	s1.familyName = "SourceFamilyName"
	if default == sourceLocation:
		s1.copyGroups = True
		s1.copyFeatures = True
		s1.copyInfo = True
	if c == 400:
		tc = "Narrow"
	elif c == 1000:
		tc = "Wide"
	else:
		tc = f"weight_{c}"
	s1.styleName = tc
	doc.addSource(s1)

# add instances
extrapolateAmount = 100
interestingWeightValues = [a1.minimum-extrapolateAmount, (400, 1200), 300, 400, 550, 700, a1.maximum, a1.maximum+extrapolateAmount]

for c in interestingWeightValues:
	s1 = InstanceDescriptor()
	s1.path = os.path.join("instances", f"geometryInstance_c_{c}.ufo")
	s1.location = dict(width=c)
	s1.familyName = "InstanceFamilyName"
	if c == 400:
		tc = "Narrow"
	elif c == 1000:
		tc = "Wide"
	else:
		tc = f"weight_{c}"
	s1.name = f"geometryInstance"
	s1.styleName = tc
	s1.kerning = True
	s1.info = True
	doc.addInstance(s1)

path = "ds4.designspace"
print(doc.formatVersion)
doc.write(path)

for s in doc.sources:
	print(s.location)

# ok. now about generating the instances.
#udoc = ufoProcessor.ufoOperator.UFOOperator(path)
#udoc.read(path)
#udoc.loadFonts()
#udoc.generateUFOs()
