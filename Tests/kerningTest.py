from fontMath.mathKerning import MathKerning

import fontMath.mathKerning
print(fontMath.mathKerning.__file__)
from defcon.objects.font import Font
from ufoProcessor.varModels import VariationModelMutator
from mutatorMath.objects.mutator import buildMutator
from fontTools.designspaceLib import AxisDescriptor

value = 1

f = Font()
f.groups["public.kern1.groupA"] = ['one', 'Bee']
f.groups["public.kern2.groupB"] = ['two', 'Three']
f.kerning[('public.kern1.groupA', 'public.kern2.groupB')] = -100
f.kerning[("one", "two")] = value

m = MathKerning(f.kerning, f.groups)
print("mathKerning object items:", m.items())
print("\tpair", ('public.kern1.groupA', 'public.kern2.groupB'), m[('public.kern1.groupA', 'public.kern2.groupB')])
print("\tpair", ('public.kern1.groupA', 'two'), m[('public.kern1.groupA', 'two')])
print("\tpair", ('one', 'public.kern2.groupB'), m[('one', 'public.kern2.groupB')])
print("\tpair", ('one', 'two'), m[('one', 'two')])

items = [(dict(w=0), m), (dict(w=1), m)]
a = AxisDescriptor()
a.name = "w"
a.minimum = 0
a.default = 0
a.maximum = 1

# process with varlib.model
mut1 = VariationModelMutator(items, [a])
m1i = mut1.makeInstance(dict(w=1))
print("\n#varlib")
print(m1i.items())

# process with mutator
bias, mut2 = buildMutator(items)
m2i = mut2.makeInstance(dict(w=1))
print("\n#mutator")
print(m2i.items())

# process with the same mathematical operations on a naked mathKerning object
m3i = m + 2* m - m - m
print("\n#raw")
print(m3i.items())
