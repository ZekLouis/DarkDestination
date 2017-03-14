#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
    Very simple game with Pygame
"""

import sys, pygame
import os
import time
import signal
from pygame.locals import *
import random
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time, sys


# Importation de la map (tableau) niveau.carte
import niveau

maps = niveau.carte


# FUNCTIONS *******************
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

# GAME CLASSES ****************
class Block(pygame.sprite.Sprite):
    """Class for block collition"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x,y,20,20)

class Soldier(pygame.sprite.Sprite):
    """Class for the player"""

    def __init__(self, number):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('Pics/survivor_e.png')
        self.orientation = 'e'
        if number == 1:
            self.rect.center = [SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2]

    def update(self, keys):
        rectx = self.rect.x
        recty = self.rect.y
        if keys[K_UP] and keys[K_LEFT]:
            self.orientation = 'nw'
            self.rect = self.rect.move([-10,-10])
        elif keys[K_UP] and keys[K_RIGHT]:
            self.orientation = 'ne'
            self.rect = self.rect.move([10,-10])
        elif keys[K_DOWN] and keys[K_LEFT]:
            self.orientation = 'sw'
            self.rect = self.rect.move([-10,10])
        elif keys[K_DOWN] and keys[K_RIGHT]:
            self.orientation = 'se'
            self.rect = self.rect.move([10,10])
        elif keys[K_UP]:
            self.orientation = 'n'
            self.rect = self.rect.move([0,-10])
        elif keys[K_DOWN]:
            self.orientation = 's'
            self.rect = self.rect.move([0,10])
        elif keys[K_LEFT]:
            self.orientation = 'w'
            self.rect = self.rect.move([-10,0])
        elif keys[K_RIGHT]:
            self.orientation = 'e'
            self.rect = self.rect.move([10,0])

        # Vérification de la position
        if pygame.sprite.spritecollide(self, MAP, False):
            #print '---COLLIDE---',self.rect.x,self.rect.y
            self.rect.x = rectx
            self.rect.y = recty

# PODSIXNET *********************
class ClientChannel(Channel):

    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def create_soldier(self, number):
        self.soldier = Soldier(number)

    def Close(self):
        self._server.del_client(self)

    def Network_keys(self,data):
        keys = data['keystrokes']
        self.soldier.update(keys)


# SERVER
class MyServer(Server):

    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.clients = []
        self.run = False
        pygame.init()
        self.screen = pygame.display.set_mode((128, 128))
        print('Server launched')

    def Connected(self, channel, addr):
        self.clients.append(channel)
        channel.create_soldier(len(self.clients))
        print('New connection: %d client(s) connected' % len(self.clients))

        if len(self.clients) == 2:
            for client in self.clients:
                client.Send({'action':'start'})
            self.run = True
            wheels_image, wheels_rect = load_png('Pics/wheels.png')
            self.screen.blit(wheels_image, wheels_rect)

    def del_client(self,channel):
        print('client deconnecte')
        self.clients.remove(channel)

    # SENDING FUNCTIONS
    def send_soldiers(self):
        while len(self.clients) != 2 :
            pass
        soldier1 = self.clients[0].soldier
        soldier2 = self.clients[1].soldier
        message1 = [ soldier1.rect.centerx, soldier1.rect.centery, soldier1.orientation ]
        message2 = [ soldier2.rect.centerx, soldier2.rect.centery, soldier2.orientation ]
        for client in self.clients:
            client.Send({'action':'soldier', 'soldier1':message1, 'soldier2':message2})

    # MAIN LOOP
    def launch_game(self):
        """Main function of the game"""

        # Init Pygame
        pygame.display.set_caption('Server')
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1,1)

        # Elements
        wait_image, wait_rect = load_png('Pics/wait.png')
        self.screen.blit(wait_image, wait_rect)

        while True:
            clock.tick(60)
            self.Pump()

            if self.run:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quitter()

                # updates
                self.send_soldiers()

            pygame.display.flip()


# PROGRAMME INIT
if __name__ == '__main__':
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    MAP = pygame.sprite.RenderClear()
    y = 0
    for ligne in maps:
        x = 0
        for char in ligne:
            if char == "#":
                block = Block(x,y)
                MAP.add(block)
                print '--ADD BLOCK--',x,':',y,'rect',block.rect
            x+=20
        y+=20
    my_server = MyServer(localaddr = (sys.argv[1],int(sys.argv[2])))
    my_server.launch_game()
