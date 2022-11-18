
p1 = ('glyphOne', 'glyphTwo')
p2 = ('glyphTwo', 'glyphOne')

g = "glyphOne"    

for f in AllFonts():
    print(f.path, f.kerning.items())
    f.kerning[p1] = f[g].width
    f.kerning[p2] = -f[g].width
    f.kerning[('glyphTwo', 'glyphTwo')] = -400
    f.kerning[('glyphOne', 'glyphOne')] = 400
    f.save()
    f.close()
    
