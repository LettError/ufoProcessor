# test the extrapolation in VariationModel

from fontTools.varLib.models import VariationModel

locations = [
    dict(wgth=0),
    dict(wght=1000),    
]

values = [10, 20]

m = VariationModel(locations, extrapolate=True)

# interpolating
assert m.interpolateFromMasters(dict(wght=0), values) == 10
assert m.interpolateFromMasters(dict(wght=500), values) == 15
assert m.interpolateFromMasters(dict(wght=1000), values) == 20

# extrapolate over max
assert m.interpolateFromMasters(dict(wght=1500), values) == 25
assert m.interpolateFromMasters(dict(wght=2000), values) == 30

# extrapolation over min gets stuck
print(m.interpolateFromMasters(dict(wght=-500), values), m.interpolateFromMasters(dict(wght=-1000), values))

# would expect:
assert m.interpolateFromMasters(dict(wght=-500), values) == -5
assert m.interpolateFromMasters(dict(wght=-1000), values) == -10

