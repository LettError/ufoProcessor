

def swapGlyphNames(font, oldName, newName, swapNameExtension = "_______________swap"):
    # In font swap the glyphs oldName and newName.
    # Also swap the names in components in order to preserve appearance.
    # Also swap the names in font groups.
    if not oldName in font or not newName in font:
        return None
    swapName = oldName + swapNameExtension
    # park the old glyph
    if not swapName in font:
        font.newGlyph(swapName)
    # get anchors
    oldAnchors = font[oldName].anchors
    newAnchors = font[newName].anchors

    # swap the outlines
    font[swapName].clear()
    p = font[swapName].getPointPen()
    font[oldName].drawPoints(p)
    font[swapName].width = font[oldName].width
    # lib?
    font[oldName].clear()
    p = font[oldName].getPointPen()
    font[newName].drawPoints(p)
    font[oldName].width = font[newName].width
    for a in newAnchors:
        na = defcon.Anchor()
        na.name = a.name
        na.x = a.x
        na.y = a.y
        # FontParts and Defcon add anchors in different ways
        # this works around that.
        try:
            font[oldName].naked().appendAnchor(na)
        except AttributeError:
            font[oldName].appendAnchor(na)

    font[newName].clear()
    p = font[newName].getPointPen()
    font[swapName].drawPoints(p)
    font[newName].width = font[swapName].width
    for a in oldAnchors:
        na = defcon.Anchor()
        na.name = a.name
        na.x = a.x
        na.y = a.y
        try:
            font[newName].naked().appendAnchor(na)
        except AttributeError:
            font[newName].appendAnchor(na)


    # remap the components
    for g in font:
        for c in g.components:
           if c.baseGlyph == oldName:
               c.baseGlyph = swapName
           continue
    for g in font:
        for c in g.components:
           if c.baseGlyph == newName:
               c.baseGlyph = oldName
           continue
    for g in font:
        for c in g.components:
           if c.baseGlyph == swapName:
               c.baseGlyph = newName

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

    remove = []
    for g in font:
        if g.name.find(swapNameExtension)!=-1:
            remove.append(g.name)
    for r in remove:
        del font[r]

