from __init__ import DesignSpaceProcessor, InstanceDescriptor


dp = "/Users/erik/code/skateboard/ufo/MutatorSans-with-intermediates.designspace"
d = DesignSpaceProcessor()
d.read(dp)

d.checkDefault()
d.loadFonts()

for s in d.sources:
	print(s.path)

names = ['S', 'K', 'A', 'T', 'E', 'B', 'O', 'A', 'R', 'D']
i = InstanceDescriptor()
i.location = d.newDefaultLocation()
r = d.makeInstance(i, glyphNames=names)
print("\n".join(d.problems))
print(r.keys())