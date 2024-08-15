[![PyPI](https://img.shields.io/pypi/v/ufoprocessor.svg)](https://pypi.org/project/ufoprocessor)

# ufoProcessor
Python package based on the **designSpaceDocument** from [fontTools.designspaceLib](https://github.com/fonttools/fonttools/tree/master/Lib/fontTools/designspaceLib)) specifically to _process_ and _generate_ instances for UFO files, glyphs and other data.

## UFOOperator takes over from UfoProcessor

Some deep changes were necessary to support designspace format 5 files. Rather than try to work it into unwilling old code, UFOOperator is rewritten from the bottom up. The new object *wraps* the FontTools DesignSpaceDocument object, rather than *subclassing* it. The goals for UFOOperator remain largely the same. Though the emphasis is now on providing objects that provide live interpolation, rather than generate stand alone UFOs.

* Support designspace format 5, with layers. *Not all elements of designspace 5 are supported.*
* Collect source materials
* Provide mutators for specific glyphs, font info, kerning so that other tools can generate partial instances. Either from `MutatorMath` or `fonttools varlib.model`.
* Support anisotropic locations in both math models, even if Variable Fonts won't. These are super useful during design, so I need them to work.
* Support extrapolation in both math models, even if Variable Fonts won't. Note that MutatorMath and VarLib approach extrapolation differently. Useful for design-explorations.
* Support discrete axes. This is a bit complex, but it is nice when it works.
* Apply avar-like designspace bending
* Generate actual UFO instances in formats 3.
* Round geometry as requested
* Try to stay up to date with fontTools
* Baseclass for tools that need access to designspace data.
* Some caching of MutatorMath and Varlib flavored mutators.

## No more rules
UFOProcessor could execute *some* of the feature-variation rules when it generated UFOs. But these variations has become much more complex than can be faked with simple glyph-swapping. So I did not port that to UFOOperator. UFOs generated with UFOOperator will have all the glyphs in the same places as their sources.

## Discrete axes
A *discrete axis* is a way to fit different interpolating systems into a single designspace. For instance a *roman* could be on ```italic=0``` and the *italic* on ```italic=1```. The roman and italic are in the same file, but to UFOOperator they are separate systems that interpolate along the normal axes. If is are more than one discrete axis in a designspace, each combination of the axis values, each *discrete location* can be an interpolating system. So some of the methods of UFOOperator require a `discrete location` to know which interpolating system is needed. 


## Examples UFOProcessor (old)

Generate all the instances (using the varlib model, no rounding):

```python
import ufoProcessor
myPath = "myDesignspace.designspace"
ufoProcessor.build(myPath)
```

Generate all the instances (using the varlib model, but round all the geometry to integers):

```python
import ufoProcessor
myPath = "myDesignspace.designspace"
ufoProcessor.build(myPath, roundGeometry=True)
```

Generate all the instances (using the mutatormath model, no rounding):

```python
import ufoProcessor
myPath = "myDesignspace.designspace"
ufoProcessor.build(myPath, useVarlib=False)
```

Generate an instance for one glyph, `"A"` at `width=100, weight=200`. (assuming the designspace has those axes and the masters have that glyph)

```python
import ufoProcessor
myPath = "myDesignspace.designspace"
doc = ufoProcessor.DesignSpaceProcessor()
doc.read(myPath)
doc.loadFonts()
glyphMutator = doc.getGlyphMutator("A")
instance = glyphMutator.makeInstance(Location(width=100, weight=200)
```

Depending on the setting for `usevarlib`, the `glyphMutator` object returned by `getGlyphMutator` in the example above can either be a `MutatorMath.Mutator`, or a `VariationModelMutator` object. That uses the `fontTools.varLib.models.VariationModel` but it is wrapped and can be called as a Mutator object to generate instances. This way `DesignSpaceProcessor` does not need to know much about which math model it is using.
