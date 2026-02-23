
import importlib
import ufoProcessor
#importlib.reload(ufoProcessor)

#importlib.reload(ufoProcessor.ufoOperator)
from ufoProcessor.ufoOperator import UFOOperator

dsPath = "/Users/erik/code/mutatorSans/MutatorSans.designspace"
ops = UFOOperator(dsPath)
ops.loadFonts(reload=True)
ops.debug = True
print(ops.instances)

ops.generateUFOs(processRules=True)

#for instanceDescriptor in ops.instances:
#    print(f'generating UFO at {instanceDescriptor.path}')
#    font = ops.makeInstance(instanceDescriptor,
#            doRules=True
#            )
#    #font.path = instanceDescriptor.path
#    print("instanceDescriptor.path", instanceDescriptor.path)
#    font.save(instanceDescriptor.path)
#    print(font.path)
                