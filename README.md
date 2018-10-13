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

* documentPath: path to the designspace file.
* outputUFOFormatVersion: integer, 2, 3. Format for generated UFOs. Note: can be different from source UFO format.
* roundGeometry: bool, if the geometry needs to be rounded to whole integers. This affects glyphs, metrics, kerning, select font info.
* processRules: bool, when generating UFOs, execute designspace rules as swaps.
* logger: optional logger object.

* documentPath:               filepath to the .designspace document
* outputUFOFormatVersion:     ufo format for output, default is the current, so 3.
* useVarlib:                  True if you want the geometry to be generated with `varLib.model` instead of `mutatorMath`.
