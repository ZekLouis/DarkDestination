#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
    Very simple game with Pygame
"""
import sys, pygame
import signal
import os
import time
from pygame.locals import *
import random
from PodSixNet.Connection import connection, ConnectionListener

# FUNCTIONS
def load_png(name):
    """Load image and return image object"""
    fullname=os.path.join('.',name)
    try:
        image=pygame.image.load(fullname)
        if image.get_alpha is None:
            image=image.convert()
        else:
            image=image.convert_alpha()
    except pygame.error:
        print('Cannot load image: %s' % name)
        raise SystemExit
    return image,image.get_rect()

def quitter():
    pygame.display.quit()
    my_pid = os.getpid()
    os.kill(my_pid,signal.SIGKILL)


# PODSIXNET
class GameClient(ConnectionListener):

    def __init__(self, host, port):
        self.Connect((host, port))
        self.run = False

	### Network event/message callbacks ###
    def Network_connected(self, data):
        print('client connecte au serveur !')

    def Network_start(self, data):
        self.run = True
        screen.blit(background_image, background_rect)

    def Network_error(self, data):
        print('error: %s', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        quitter()


# CLASSES
class Soldier(pygame.sprite.Sprite, ConnectionListener):
    """Class for the player"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        """
        self.images = []
        self.rects = []
        self.image, self.rect = load_png('Pics/survivor_e.png')
        """


        """
        self.images.append(image)
        self.rects.append(rect)
        image, rect = load_png('Pics/survivor_move/survivor-move_rifle_1.png')
        self.images.append(image)
        self.rects.append(rect)
        """




        """
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.rects[self.index]
        """
        self.image, self.rect = load_png('Pics/survivor_e.png')
        self.image_n,_ = load_png("Pics/survivor_n.png")
        self.image_s,_ = load_png("Pics/survivor_s.png")
        self.image_w,_ = load_png("Pics/survivor_w.png")
        self.image_e,_ = load_png("Pics/survivor_e.png")
        self.image_n_e,_ = load_png("Pics/survivor_n_e.png")
        self.image_s_e,_ = load_png("Pics/survivor_s_e.png")
        self.image_n_w,_ = load_png("Pics/survivor_n_w.png")
        self.image_s_w,_ = load_png("Pics/survivor_s_w.png")
        self.rect.center = [ SCREEN_WIDTH/2 +100, SCREEN_HEIGHT/2 ]
        self.orientation = 'e'

    def Network_soldier(self,data):
        self.orientation = data['soldier1'][2]
        if self.orientation == 'n':
            self.image = self.image_n
        elif self.orientation == 's':
            self.image = self.image_s
        elif self.orientation == 'w':
            self.image = self.image_w
        elif self.orientation == 'e':
            self.image = self.image_e
        elif self.orientation == 'ne':
            self.image = self.image_n_e
        elif self.orientation == 'nw':
            self.image = self.image_n_w
        elif self.orientation == 'se':
            self.image = self.image_s_e
        elif self.orientation == 'sw':
            self.image = self.image_s_w
        self.rect.center = data['soldier1'][0:2]


    def update(self):
        self.Pump()

    def getImage(self):
        return self.image

    def getRect(self):
        return self.rect


class Soldier2(pygame.sprite.Sprite, ConnectionListener):
    """Class for the player"""

    def __init__(self):
    	pygame.sprite.Sprite.__init__(self)
    	self.image,self.rect=load_png("Pics/soldier_n.png")
    	self.image_n,_ = load_png("Pics/soldier_n.png")
    	self.image_s,_ = load_png("Pics/soldier_s.png")
    	self.image_w,_ = load_png("Pics/soldier_w.png")
    	self.image_e,_ = load_png("Pics/soldier_e.png")
        self.rect.center = [ SCREEN_WIDTH/2 -100, SCREEN_HEIGHT/2 ]
        self.orientation = 'n'

    def Network_soldier(self,data):
        self.orientation = data['soldier2'][2]
        if self.orientation == 'n':
            self.image = self.image_n
        elif self.orientation == 's':
            self.image = self.image_s
        elif self.orientation == 'w':
            self.image = self.image_w
        elif self.orientation == 'e':
            self.image = self.image_e
        self.rect.center = data['soldier2'][0:2]


    def update(self):
        self.Pump()

    def getImage(self):
        return self.image

    def getRect(self):
        return self.rect

# MAIN
if __name__ == '__main__':
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768

    pygame.display.set_caption('Dark Destination')

    # PodSixNet init
    game_client = GameClient(sys.argv[1],int(sys.argv[2]))

    # Init Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.key.set_repeat(1,1)

    # Elements
    background_image, background_rect = load_png('Pics/map.png')
    background_image = pygame.transform.scale(background_image, (background_rect.width*2,background_rect.height*2))


    # background_image = pygame.transform.scale2x(background_image)
    wait_image, wait_rect = load_png('Pics/wait1.png')
    wait_rect.center = [ SCREEN_WIDTH/2, SCREEN_HEIGHT/2 ]
    screen.blit(background_image, background_rect)


    soldier_sprite = pygame.sprite.RenderClear()

    soldier_sprite.add(Soldier())
    soldier_sprite.add(Soldier2())

    while True:
        clock.tick(60)
        connection.Pump()
        game_client.Pump()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitter()

        if game_client.run:
            keys = pygame.key.get_pressed()
            if keys[K_q]:
                quitter()
            connection.Send({'action':'keys','keystrokes':keys})

            # updates
            soldier_sprite.update()

            # drawings
            # background_rect = background_rect.move([2,2])

            screen.fill((0,0,0))



            background_rect = background_rect.move([10,10])
            screen.blit(background_image, background_rect)


            for soldier in soldier_sprite:
                screen.blit(soldier.getImage(),soldier.getRect())

            # soldier_sprite.clear(screen, background_image)
            # soldier_sprite.draw(screen)

        else: # game is not running
            screen.blit(wait_image, wait_rect)

        pygame.display.flip()
