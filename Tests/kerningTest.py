from fontMath.mathKerning import MathKerning

import fontMath.mathKerning
print(fontMath.mathKerning.__file__)
from defcon.objects.font import Font
from ufoProcessor.varModels import VariationModelMutator
from mutatorMath.objects.mutator import buildMutator
from ufoProcessor.designspaceLib import AxisDescriptor

value = 0

f = Font()
f.groups["public.kern1.groupA"] = ['one', 'Bee']
f.groups["public.kern2.groupB"] = ['two', 'Three']
f.kerning[('public.kern1.groupA', 'public.kern2.groupB')] = -100
f.kerning[("one", "two")] = value

m = MathKerning(f.kerning, f.groups)
print("Font_defcon	 before", m.items())

print("pair", m[('public.kern1.groupA', 'public.kern2.groupB')])
print("pair", m[('public.kern1.groupA', 'two')])
print("pair", m[('one', 'public.kern2.groupB')])
print("pair", m[('one', 'two')])

items = [(dict(w=0), m), (dict(w=1), m)]
a = AxisDescriptor()
a.name = "w"
a.minimum = 0
a.default = 0
a.maximum = 1

mut1 = VariationModelMutator(items, [a])
m1i = mut1.makeInstance(dict(w=1))
print(m1i.items())

bias, mut2 = buildMutator(items)
m2i = mut2.makeInstance(dict(w=1))
print(m2i.items())
