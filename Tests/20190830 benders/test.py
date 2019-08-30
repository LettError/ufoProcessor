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


"""

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
print(dsc.hasStructuralProblems())


print(dp.newDefaultLocation())
print(dp.instances)
print('findDefault', dp.findDefault())
dp.useVarlib = True
print('varlib', dp.useVarlib)

default = dp.getNeutralFont()
print(default.path)
dp.generateUFO(bend=False)

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
