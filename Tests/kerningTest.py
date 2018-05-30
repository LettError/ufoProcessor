from fontMath.mathKerning import MathKerning
from fontParts.fontshell import RFont as Font_fontParts
from defcon.objects.font import Font as Font_defcon

value = 0

f = Font_fontParts()
f.groups["public.kern1.groupA"] = ['one', 'Bee']
f.groups["public.kern2.groupB"] = ['two', 'Three']
f.kerning[('public.kern1.groupA', 'public.kern2.groupB')] = -100
f.kerning[("one", "two")] = value

m = MathKerning(f.kerning, f.groups)
print("Font_fontParts before", m.items())

m = m * 2 - m
print("Font_fontParts after", m.items())



f = Font_defcon()
f.groups["public.kern1.groupA"] = ['one', 'Bee']
f.groups["public.kern2.groupB"] = ['two', 'Three']
f.kerning[('public.kern1.groupA', 'public.kern2.groupB')] = -100
f.kerning[("one", "two")] = value


m = MathKerning(f.kerning, f.groups)
print("Font_defcon before", m.items())

print("pair", m[('public.kern1.groupA', 'public.kern2.groupB')])
print("pair", m[('public.kern1.groupA', 'two')])
print("pair", m[('one', 'public.kern2.groupB')])
print("pair", m[('one', 'two')])

m = m * 2 - m
print("Font_defcon after", m.items())

