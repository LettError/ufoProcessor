
name = "glyphTwo"

for f in AllFonts():
    
    f.newGlyph(name)
    f[name].appendComponent("glyphOne")
    f[name].width = f['glyphOne'].width
    f.save()