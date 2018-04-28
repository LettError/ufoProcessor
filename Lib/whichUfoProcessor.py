import sys
for s in sys.path:
    print(s)
    if "ufoProcessor" in s:
        print('\t',s)
    
import ufoProcessor
print(ufoProcessor.__file__)