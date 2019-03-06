
# interesting problem with mathInfo objects
# when processing attributes that do not exist in the other object.
# This can happen when one of the masters has more values set than the other. 
# For instance when preparing the "deltas", the objects with relative data

# In these tests mathINfo objects are added, multiplied and subtracted
# None - value, None + value, value + value and None + None

from fontParts.world import RFont
from fontMath import MathInfo
import fontMath

ok = "✅"
notOk = "🚫"

def extractValue(m, attrName, expected=None):
	f = RFont()
	f.info.fromMathInfo(m)
	v = getattr(f.info, attrName)
	if v == expected:
		t = ok
	else:
		t = notOk
	print("\t", t, v, "\t", attrName)

# master 1
f1 = RFont()
f1.info.ascender = 800					# present in both masters
f1.info.openTypeHheaAscender = 330		# example value that won't be in master 2
m1 = f1.info.toMathInfo()

f2 = RFont()
f2.info.ascender = 750					# present in both masters
f2.info.openTypeOS2TypoAscender = 555	# example value that won't be in master 1

m2 = f2.info.toMathInfo()

# subtraction
m3 = m1 - m2

print("\nm1 \"default\"")
extractValue(m1, "ascender", 800)
extractValue(m1, "openTypeOS2TypoAscender", None)
extractValue(m1, "openTypeHheaAscender", 330)

print("\nm2")
extractValue(m2, "ascender", 750)
extractValue(m2, "openTypeOS2TypoAscender", 555)
extractValue(m2, "openTypeHheaAscender", None)	# not set

print("\nm3 = m1 - m2")
extractValue(m3, "ascender", 50)
extractValue(m3, "openTypeOS2TypoAscender", 0)
extractValue(m3, "openTypeHheaAscender", 0)


# addition
m3b = m1 + m2
print("\nm3b = m1 + m2")
extractValue(m3b, "ascender", 1550)
extractValue(m3b, "openTypeOS2TypoAscender", 555)	 # None + 555
extractValue(m3b, "openTypeHheaAscender", 330)

m3c = m1 + m1
print("\nm3c = m1 + m1")
extractValue(m3c, "ascender", 1600)
extractValue(m3c, "openTypeOS2TypoAscender", None)	# None + None
extractValue(m3c, "openTypeHheaAscender", 660) # 330 + 330

m3d = m2 + m2
print("\nm3d = m2 + m2")
extractValue(m3d, "ascender", 1500)
extractValue(m3d, "openTypeOS2TypoAscender", 1110)	# 555 + 555
extractValue(m3d, "openTypeHheaAscender", None) # None + None

m3e = m2 - m2
print("\nm3e = m2 - m2")
extractValue(m3e, "ascender", 0)
extractValue(m3e, "openTypeOS2TypoAscender", 0)	# 555 - 555
extractValue(m3e, "openTypeHheaAscender", None) # None - None

m3f = m1 - m1
print("\nm3e = m1 - m1")
extractValue(m3f, "ascender", 0)
extractValue(m3f, "openTypeOS2TypoAscender", None)	# None - None
extractValue(m3f, "openTypeHheaAscender", 0) # 330 - 330

# if     c = a - b
# then   a = c + b

m4 = m3 + m2
print("\nm4 = m3 + m2")
extractValue(m4, "ascender", 800)
extractValue(m4, "openTypeOS2TypoAscender", 555)
extractValue(m4, "openTypeHheaAscender", 0)


m5 = .5 * m1
m6 = 2 * m5
print("\nm5 half")
extractValue(m5, "ascender", 400)
extractValue(m5, "openTypeOS2TypoAscender", None)
extractValue(m5, "openTypeHheaAscender", 165)
print("\nm6 duped again")
extractValue(m6, "ascender", 800)
extractValue(m6, "openTypeOS2TypoAscender", None)
extractValue(m6, "openTypeHheaAscender", 330)


f = .6666
m7 = m1 + f * (m2-m1)
print("\nm7 interpolated with %3.3f" % f)
extractValue(m7, "ascender", 766.67)
extractValue(m7, "openTypeOS2TypoAscender", 0)
extractValue(m7, "openTypeHheaAscender", 330)


# maybe it should be like this:
# <value a> - <unknown b> = 0
# <value a> + <unknown b> = <value a>

# <unknown a> - <value b> = 0
# <unknown a> + <value b> = <value a>

# scalar * <unknown b> = <unknown b>
# <unknown b> / factor = <unknown b>

# This works in mutatormath as it started with the actual default object
# but varlib starts with the esult of 1.0 * default object.
# 