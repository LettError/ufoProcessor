import designspaceProblems
print(designspaceProblems.__file__)

path= "ds5.designspace"
checker = designspaceProblems.DesignSpaceChecker(path)
checker.checkEverything()
print(checker.checkDesignSpaceGeometry())
checker.checkSources()
checker.checkInstances()
print("hasStructuralProblems", checker.hasStructuralProblems())

print(checker.problems)