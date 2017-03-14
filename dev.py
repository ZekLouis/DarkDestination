import niveau

maps = niveau.carte

y=0
for ligne in maps:
    x = 0
    for char in ligne:
        if char == "#":
            print x,':',y
        x+=10
    y+=10
