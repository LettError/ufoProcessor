import os
import plistlib
import ufoLib

def getUFOVersion(ufoPath):
    # <?xml version="1.0" encoding="UTF-8"?>
    # <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    # <plist version="1.0">
    # <dict>
    #   <key>creator</key>
    #   <string>org.robofab.ufoLib</string>
    #   <key>formatVersion</key>
    #   <integer>2</integer>
    # </dict>
    # </plist>
    metaInfoPath = os.path.join(ufoPath, u"metainfo.plist")
    p = plistlib.readPlist(metaInfoPath)
    return p.get('formatVersion')

def getUFOLayers(ufoPath):
    # get the contents of the layerContents
    reader = ufoLib.UFOReader(ufoPath)
    return reader.getLayerNames()

ufoPath = "/Users/erik/Toolsketches/20161206 Gauges/LayeredGauge.ufo"
print(getUFOVersion(ufoPath))
print(getUFOLayers(ufoPath))