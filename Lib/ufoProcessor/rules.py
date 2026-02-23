from fontTools.pens.recordingPen import RecordingPointPen

def swapGlyphNames(font, oldName, newName):
    # In font swap the glyphs oldName and newName.
    # Also swap the names in components in order to preserve appearance.
    # Also swap the names in font groups.
    if not oldName in font or not newName in font:
        return None
    
    oldRecording = RecordingPointPen()
    newRecording = RecordingPointPen()
    
    oldGlyph = font[oldName]
    newGlyph = font[newName]
    
    oldGlyph.drawPoints(oldRecording)
    newGlyph.drawPoints(newRecording)
    
    # swap widths    
    oldGlyph.width, newGlyph.width = newGlyph.width, oldGlyph.width

    # swap the glyph objects
    oldGlyph.clear()
    newGlyph.clear()
    
    oldRecording.replay(newGlyph.getPointPen())
    newRecording.replay(oldGlyph.getPointPen())

    # remap the components
    for g in font:
        for c in g.components:
           if c.baseGlyph == oldName:
               c.baseGlyph = newName
           elif c.baseGlyph == newName:
               c.baseGlyph = oldName
        g.changed()
    
    # change the names in groups
    # the shapes will swap, that will invalidate the kerning
    # so the names need to swap in the kerning as well.
    newKerning = {}
    for first, second in font.kerning.keys():
        value = font.kerning[(first,second)]
        if first == oldName:
            first = newName
        elif first == newName:
            first = oldName
        if second == oldName:
            second = newName
        elif second == newName:
            second = oldName
        newKerning[(first, second)] = value
    font.kerning.clear()
    font.kerning.update(newKerning)

    for groupName, members in font.groups.items():
        newMembers = []
        for name in members:
            if name == oldName:
                newMembers.append(newName)
            elif name == newName:
                newMembers.append(oldName)
            else:
                newMembers.append(name)
        font.groups[groupName] = newMembers

    
    
#swapGlyphNames(CurrentFont(), "B", "B.alt")
#swapGlyphNames(CurrentFont(), "B.alt", "B")