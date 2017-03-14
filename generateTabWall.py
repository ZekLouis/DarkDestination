#! /usr/bin/env python
import pygame
import os
pygame.font.init()
default_font = pygame.font.get_default_font()
font_renderer = pygame.font.Font(default_font, 20)

# Chargement du fond.
backgroundImg = pygame.image.load("Pics/map.png")

width = backgroundImg.get_rect().size[0]
height = backgroundImg.get_rect().size[1]

size = 10
xNbr = width/size
yNbr = height/size

# Creation de la fenetre.
screen = pygame.display.set_mode((width, height))

# Creation du fond.
background = pygame.Surface((width, height))
background.blit(backgroundImg, (0, 0))

for i in range(xNbr):
    pygame.draw.line(background, (150, 0, 0), (i*size, 0), (i*size, height), 1)
for j in range(yNbr):
    pygame.draw.line(background, (150, 0, 0), (0, j*size), (width, j*size), 1)

# Creation de la grille.
grid = pygame.Surface((width, height))
grid.set_alpha(64)
grid.fill((255, 255, 255))

# Carte.
map = []
for i in range(yNbr):
    map.append(" "*xNbr)

# Boucle de rendu.
clock = pygame.time.Clock()
spaceMode = "doNothing"
running = 1
while running:
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.KEYDOWN:
            spaceMode = "write" if spaceMode == "doNothing" else "doNothing" if spaceMode == "erase" else "erase"

        if event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            if spaceMode != "doNothing":
                char = "#" if spaceMode == "write" else " "

                y = (int)(pos[1]/size)
                x = (int)(pos[0]/size)

                ls = list(map[y])
                ls[x] = char
                map[y] = ''.join(ls)

                if char == "#":
                    pygame.draw.rect(grid, (0, 0, 0), (x*size, y*size, 10, 10))
                else :
                    pygame.draw.rect(grid, (255, 255, 255), (x*size, y*size, 10, 10))

        if event.type == pygame.QUIT:
            running = 0

    screen.blit(background, (0,0))
    screen.blit(grid, (0,0))

    label = font_renderer.render(
        spaceMode,   # The font to render
        1,             # With anti aliasing
        (0,0,0)) # RGB Color

    screen.blit(label, (10, height - 40))

    pygame.display.flip()
    clock.tick(1000./60.)

file = open("niveau.py", "wrb+")

file.write("carte = [")

for line in map:
    file.write("\n\t'"+line+"',")

file.seek(-1, os.SEEK_END)
file.truncate()

file.write("\n]")
