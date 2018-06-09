from fontMath.mathKerning import MathKerning

import fontMath.mathKerning
from defcon.objects.font import Font
from fontParts.fontshell import RFont
from ufoProcessor.varModels import VariationModelMutator
from mutatorMath.objects.mutator import buildMutator
from fontTools.designspaceLib import AxisDescriptor

# kerning exception value. Different results for 1 and 0
value = 0 

#f = Font()
f = RFont()		# doesn't make a difference
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
v = None
deltas = [m, m]
scalars = [1.0, 1.0]
assert len(deltas) == len(scalars)
for i,(delta,scalar) in enumerate(zip(deltas, scalars)):
	if not scalar: continue
	contribution = delta * scalar
	if v is None:
		v = contribution
	else:
		v += contribution
print("\n#doing the math that varlib does")
print(v.items())

print(m.groups())
print((m*2.0).groups())
