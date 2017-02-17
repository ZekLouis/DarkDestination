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
import time,sys



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
class Soldier(pygame.sprite.Sprite):
    """Class for the player"""

    def __init__(self, number):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('Pics/soldier_n.png')
        self.orientation = 'n'
        if number == 1:
            self.rect.center = [SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2]

    def update(self, keys):
        if keys[K_UP]:
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
    my_server = MyServer(localaddr = (sys.argv[1],int(sys.argv[2])))
    my_server.launch_game()
