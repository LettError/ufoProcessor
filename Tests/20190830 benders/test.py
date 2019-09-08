"""


	test with these 3 masters
	on 1 axis that has a map that maps to a different range

	axis values are in user coordinates
	designpsace problems should check with the proper mapped values
	masters and instancees are in designspace coordinates

	goals:
	* the designspace should validate
	* the generated intermediate should have touching shapes, just like master 2
	* determine if we can get rid of the bend=True/False flags

    Suppose the numbers in an axis map are messed up, it's then impossible
    to find the default.
"""

import importlib
import ufoProcessor
importlib.reload(ufoProcessor)


import mutatorMath
print(mutatorMath.__file__)
import mutatorMath.objects.mutator
importlib.reload(mutatorMath.objects.mutator)
from mutatorMath.objects.mutator import Location
from designspaceProblems import DesignSpaceChecker
import collections
from ufoProcessor import DesignSpaceProcessor
from pprint import pprint

path = "Test.designspace"

dp = DesignSpaceProcessor()
dp.read(path)
dp.loadFonts()

dsc = DesignSpaceChecker(dp)
dsc.checkEverything()
pprint(dsc.problems)
print('hasStructuralProblems', dsc.hasStructuralProblems())


print(dp.newDefaultLocation())
print(dp.instances)
print('findDefault', dp.findDefault())
dp.useVarlib = False
print('varlib', dp.useVarlib)

axisMapper = ufoProcessor.varModels.AxisMapper(dp.axes)
print('axisMapper', axisMapper.getMappedAxisValues())
r = axisMapper(Location(test=1))

default = dp.getNeutralFont()
print('default.path', default.path)
dp.generateUFO()

glyphName = "a"
print('mutator for a', dp.getGlyphMutator(glyphName))
print('-'*40)
print('problems')
for p in dp.problems:
	print(p)
print('-'*40)
print('toollog')
for line in dp.toolLog:
	print("\t" + line)


instancePath = "instances/BenderTest-Intermediate.ufo"
instance = RFont(instancePath, showUI=False)
print(instance.info.capHeight)
print(instance.kerning.items())

from mutatorMath.objects.mutator import Location
l = Location(test=0)
print(l.isOrigin())