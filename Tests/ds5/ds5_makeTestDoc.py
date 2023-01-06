# make a test designspace format 5 with 1 continuous and 2 discrete axes.

# axis width is a normal interpolation with a change in width
# axis DSC1 is a discrete axis showing 1, 2, 3 items in the glyph
# axis DSC2 is a discrete axis showing a solid or outlined shape

from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, InstanceDescriptor, AxisDescriptor, RuleDescriptor, processRules, DiscreteAxisDescriptor
from fontTools.designspaceLib.split import splitInterpolable

import os
import fontTools
print(fontTools.version)

import ufoProcessor
print(ufoProcessor.__file__)

doc = DesignSpaceDocument()

#https://fonttools.readthedocs.io/en/latest/designspaceLib/python.html#axisdescriptor
a1 = AxisDescriptor()
a1.minimum = 400
a1.maximum = 1000
a1.default = 400
a1.map = ((400,400), (700,900), (1000,1000))
a1.name = "width"
a1.tag = "wdth"
a1.axisOrdering = 1
doc.addAxis(a1)

a2 = DiscreteAxisDescriptor()
a2.values = [1, 2, 3]
a2.default = 1
a2.name = "countedItems"
a2.tag = "DSC1"
a2.axisOrdering = 2
doc.addAxis(a2)

a3 = DiscreteAxisDescriptor()
a3.values = [0, 1]
a3.default = 0
a3.name = "outlined"
a3.tag = "DSC2"
a3.axisOrdering = 3
doc.addAxis(a3)

default = {a1.name: a1.default, a2.name: a2.default, a3.name: a3.default}

# add sources


# public.skipExportGlyphs

for c in [a1.minimum, a1.maximum]:
	for d1 in a2.values:
		for d2 in a3.values:

			s1 = SourceDescriptor()
			s1.path = os.path.join("sources", f"geometrySource_c_{c}_d1_{d1}_d2_{d2}.ufo")
			s1.name = f"geometrySource{c} {d1} {d2}"
			sourceLocation = dict(width=c, countedItems=d1, outlined=d2)
			s1.location = sourceLocation
			s1.kerning = True
			s1.familyName = "SourceFamilyName"
			if default == sourceLocation:
				s1.copyGroups = True
				s1.copyFeatures = True
				s1.copyInfo = True
			td1 = ["One", "Two", "Three"][(d1-1)]
			if c == 400:
				tc = "Narrow"
			elif c == 1000:
				tc = "Wide"
			if d2 == 0:
				td2 = "solid"
			else:
				td2 = "open"
			s1.styleName = f"{td1}{tc}{td2}"
			doc.addSource(s1)

def ip(a,b,f):
	return a + f*(b-a)

# add instances
steps = 8
extrapolateAmount = 100


interestingWeightValues = [(400, 700), 300, 400, 550, 700, 1000, 1100]

mathModelPrefKey = "com.letterror.mathModelPref"
mathModelVarlibPref = "previewVarLib"
mathModelMutatorMathPref = "previewMutatorMath"

#      <key>com.letterror.mathModelPref</key>
#      <string>previewVarLib</string>


for c in interestingWeightValues:
	for d1 in a2.values:
		for d2 in a3.values:

			s1 = InstanceDescriptor()
			s1.path = os.path.join("instances", f"geometryInstance_c_{c}_d1_{d1}_d2_{d2}.ufo")
			s1.location = dict(width=c, countedItems=d1, outlined=d2)
			s1.familyName = "InstanceFamilyName"
			td1 = ["One", "Two", "Three"][(d1-1)]
			if c == 400:
				tc = "Narrow"
			elif c == 1000:
				tc = "Wide"
			if d2 == 0:
				td2 = "Solid"
			else:
				td2 = "Open"
			s1.name = f"geometryInstance {td1} {tc} {td2}"
			s1.styleName = f"{td1}{tc}{td2}"
			s1.kerning = True
			s1.info = True
			doc.addInstance(s1)

# add variable font descriptors

splits = splitInterpolable(doc)
for discreteLocation, subSpace in splitInterpolable(doc):
    print(discreteLocation, subSpace)

#print(doc.getVariableFonts())

#for item in doc.getVariableFonts():
#    doc.addVariableFont(item)

doc.variableFonts.clear()
print(doc.variableFonts)


variableFonts = doc.getVariableFonts()
print("variableFonts", variableFonts)

doc.addVariableFont(variableFonts[0])

for i, item in enumerate(variableFonts):
    print(i, item)


path = "ds5.designspace"
print(doc.lib)
doc.write(path)
print(dir(doc))


for a in doc.axes:
	if hasattr(a, "values"):
		print(a.name, "d", a.values)
	else:
		print(a.name, "r", a.minimum, a.maximum)
	
for s in doc.sources:
	print(s.location)

# ok. now about generating the instances.

udoc = ufoProcessor.DesignSpaceProcessor()
udoc.read(path)
