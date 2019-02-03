[![Travis](https://travis-ci.org/LettError/ufoProcessor.svg?branch=master)](https://travis-ci.org/LettError/ufoProcessor)
[![PyPI](https://img.shields.io/pypi/v/ufoprocessor.svg)](https://pypi.org/project/ufoprocessor)

# ufoProcessor
Python package based on the **designSpaceDocument** from [fontTools.designspaceLib](https://github.com/fonttools/fonttools/tree/master/Lib/fontTools/designspaceLib)) specifically to _process_ and _generate_ instances for UFO files, glyphs and other data.

* Collect source materials
* Provide mutators for specific glyphs, font info, kerning so that other tools can generate partial instances. Either from `MutatorMath` or `fonttools varlib.model`.
* Support designspace format 4 with layers.
* Apply avar-like designspace bending
* Apply rules
* Generate actual UFO instances in formats 2 and 3.
* Round geometry as requested
* Try to stay up to date with fontTools
* Baseclass for tools that need access to designspace data.

## Usage
The easiest way to use ufoProcessor is to call `build(designspacePath)`

* **documentPath**: path to the designspace file.
* **outputUFOFormatVersion**: integer, 2, 3. Format for generated UFOs. Note: can be different from source UFO format.
* **roundGeometry**: bool, if the geometry needs to be rounded to whole integers. This affects glyphs, metrics, kerning, select font info.
* **processRules**: bool, when generating UFOs, execute designspace rules as swaps.
* **logger**: optional logger object.

* **documentPath**:               filepath to the .designspace document
* **outputUFOFormatVersion**:     ufo format for output, default is the current, so 3.
* **useVarlib**:                  True if you want the geometry to be generated with `varLib.model` instead of `mutatorMath`.

## Convert Superpolator to designspace

The ufoProcessor.sp3 module has some tools for interpreting Superpolator .sp3 documents. Not all data is migrated. But the important geometry is there. Given that Superpolator can read designspace files, there is hopefully no real need for a writer. Note that this conversion is lossy. 

* Axis
	* dimensions
	* name
	* tag
* Source
	* ufo path
	* familyname, stylename
	* mute state (stored in lib)
	* location
* Instance
	* ufo path
	* familyname, stylename
	* stylemap names
	* location
* Rules
	* *Simple Rules* are wrapped in a conditionset.
	* most of the really old Superpolator rules can't be converted. Only rules with `<` or `>` operators are used.
* Some Superpolator user prefs
	* Preview text
	* Which axes used vertically and horizontally


## Usage 
```python
# convert sp3 file to designspace
# first make a new designspace doc object
doc = DesignSpaceDocument()
# feed it to the reader
reader = SuperpolatorReader(sp3path, doc)
reader.read()
# now you can work with it, even save it
doc.write(designspacePath)
```
Indeed that last example comes from this convenience function:  
```sp3_to_designspace(sp3path, designspacePath=None)```
If designspacePath = None, sp3_to_designspace will use the same path for the output, but replace the `.sp3` with `.designspace` extension. If the file exists it will overwrite.

## Notes
* Glyph-specific masters in instances are ignored.   
* Instance notes are ignored. 
* Designspace geometry requires the default master to be on the default value of each axis. Superpolator handled that differently, it would find the default dynamically. So it is possible that converted designspaces need some work in terms of the basic structure. That can't be handled automatically.
