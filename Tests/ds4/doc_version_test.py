# test designspacedocument versioning

from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, InstanceDescriptor, AxisDescriptor, RuleDescriptor, processRules, DiscreteAxisDescriptor

doc = DesignSpaceDocument()
doc.formatVersion = "4.0"
print(doc.formatTuple)

a1 = AxisDescriptor()
a1.minimum = 400
a1.maximum = 1000
a1.default = 400
#a1.map = ((400,400), (700,900), (1000,1000))
a1.name = "width"
a1.tag = "wdth"
#a1.axisOrdering = 1
doc.addAxis(a1)

path = "ds4_version_test.designspace"
print(doc.formatTuple)
doc.write(path)
