from fontMath.mathKerning import MathKerning
from defcon.objects.font import Font

f = Font()
f.groups["public.kern1.groupA"] = ['one', 'Bee']
f.groups["public.kern2.groupB"] = ['two', 'Three']
f.kerning[('public.kern1.groupA', 'public.kern2.groupB')] = -100
f.kerning[('one', 'two')] = 0
m = MathKerning(f.kerning, f.groups)

print(m.items())
print((m*1.0).items())


