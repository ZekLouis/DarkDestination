#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
    Very simple game with Pygame
"""

import sys, pygame
import os
import time
import signal
from random import randint
from pygame.locals import *
import random
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from vector2D import Vec2d


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

"""Test collide sprite"""
def getCaseMap(x,y):
    return maps[int(y/20)][int(x/20)] == "#"


"""Cette fonction permet de retourner le vecteur directeur que le zombie doit suivre pour être attiré"""
def getVecteurDirecteur(pointA, pointB, recur):

    if recur==0:
        return False

    dist = pointB.get_distance(pointA)
    vectDirecteurAB = (pointB - pointA).normalized()
    pasDeCollision = True

    i = 1
    while i < dist/20 and pasDeCollision:
        somme = pointA + (vectDirecteurAB * (20 * i))
        if getCaseMap(somme.x, somme.y):
            pasDeCollision = False
        i += 1

    if pasDeCollision :
        return vectDirecteurAB

    vectDirecteurBissectrice = vectDirecteurAB.perpendicular()

    for i in range(-3,3):
        pointC = pointA + (vectDirecteurAB * (dist/2)) + vectDirecteurBissectrice * (i * (dist/3))
        vectAC = getVecteurDirecteur(pointA, pointC, recur - 1)
        vectCB = getVecteurDirecteur(pointC, pointB, recur - 1)

        if vectAC and vectCB:
            return vectAC

    return False


def quitter():
    pygame.display.quit()
    my_pid = os.getpid()
    os.kill(my_pid,signal.SIGKILL)

# GAME CLASSES ****************
class SpawnSoldier(pygame.sprite.Sprite):
    """Class for object of spawn"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

class SpawnZombie(pygame.sprite.Sprite):
    """Class for object of spawn of the zombies"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

class Block(pygame.sprite.Sprite):
    """Class for block collition"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x,y,20,20)

class Sprite(pygame.sprite.Sprite):

    def __init__(self, vec):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(vec.x,vec.y,1,1)

class Zombie(pygame.sprite.Sprite):
    """Class for the zombie"""

    def __init__(self, spawnNumber, id):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('Pics/zombie_e.png')
        self.orientation = 'e'
        self.id = id
        randspawn = randint(0,len(SPAWNZOMBIE)-1)
        self.rect.x = SPAWNZOMBIE[spawnNumber].getX()
        self.rect.y = SPAWNZOMBIE[spawnNumber].getY()

    def update(self, soldier):

        vectDir = getVecteurDirecteur(Vec2d(self.rect.x,self.rect.y),Vec2d(soldier.getX(),soldier.getY()),3)
        print '--VEC--',vectDir
        if vectDir:
            self.rect.x += vectDir.x*3
            self.rect.y += vectDir.y*3


        rectx = self.rect.x
        recty = self.rect.y
        """
        #orientations = ['n', 's', 'e', 'w']
        #newOrientation = random.choice(orientations)

        if newOrientation=='n':
            self.orientation = 'n'
            self.rect = self.rect.move([0,-1])
        elif newOrientation=='s':
            self.orientation = 's'
            self.rect = self.rect.move([0,1])
        elif newOrientation=='w':
            self.orientation = 'w'
            self.rect = self.rect.move([-1,0])
        elif newOrientation=='e':
            self.orientation = 'e'
            self.rect = self.rect.move([1,0])

        if self.rect.x > soldier.getX():
            self.rect = self.rect.move([-1,0])
        else:
            self.rect = self.rect.move([1,0])

        if self.rect.y > soldier.getY():
            self.rect = self.rect.move([0,-1])
        else :
            self.rect = self.rect.move([0,1])
        """

        # Vérification de la position
        if pygame.sprite.spritecollide(self, MAP, False):
            #print '---COLLIDE---',self.rect.x,self.rect.y
            self.rect.x = rectx
            self.rect.y = recty

    def getId(self):
        return self.id



class Soldier(pygame.sprite.Sprite):
    """Class for the player"""

    def __init__(self, number):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('Pics/survivor_e.png')
        self.orientation = 'e'
        if number == 1:
            self.rect.x = SPAWNSOLDIER[0].getX()
            self.rect.y = SPAWNSOLDIER[0].getY()
        else :
            self.rect.x = SPAWNSOLDIER[1].getX()
            self.rect.y = SPAWNSOLDIER[1].getY()

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

    def getX(self):
        return self.rect.x

    def getY(self):
        return self.rect.y


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

            self.zombies = []

            for i in range(0,1):
                randspawn = randint(0,len(SPAWNZOMBIE)-1)
                nouveau_zombie = Zombie(randspawn, len(self.zombies))
                self.zombies.append(nouveau_zombie)

            for client in self.clients:
                for zombie in self.zombies:
                    message = [ zombie.rect.centerx, zombie.rect.centery, zombie.orientation ]
                    client.Send({'action':'zombie','id':zombie.getId(),'message':message})

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

    def send_zombies(self):
        for zombie in self.zombies:
            zombie.update(self.clients[0].soldier)
        for client in self.clients:
            for zombie in self.zombies:
                message = [ zombie.rect.centerx, zombie.rect.centery, zombie.orientation ]
                client.Send({'action':'zombieMouvements','id':zombie.getId(),'message':message})

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
                self.send_zombies()

            pygame.display.flip()


# PROGRAMME INIT
if __name__ == '__main__':
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    # Initialisation du groupe contenant chaque sprite simulant les murs
    MAP = pygame.sprite.RenderClear()
    # Initialisation du groupe contenant les différents spawns pour les soldiers
    SPAWNSOLDIER = []
    # Initialisation du groupe contenant les différents spawns pour les zombies
    SPAWNZOMBIE = []
    y = 0
    for ligne in maps:
        x = 0
        for char in ligne:
            if char == "#":
                block = Block(x,y)
                MAP.add(block)
                #print '--ADD BLOCK--',x,':',y,'rect',block.rect
            elif char == "S":
                spawn = SpawnSoldier(x,y)
                SPAWNSOLDIER.append(spawn)
                #print '--ADD SPAWN SOLDIER--',x,':',y,'rect',block.rect
            elif char == "Z":
                spawn = SpawnZombie(x,y)
                SPAWNZOMBIE.append(spawn)
                #print '--ADD SPAWN ZOMBIE--',x,':',y,'rect',block.rect
            x+=20
        y+=20

    print len(MAP),"BLOCK SPAWNED"
    print len(SPAWNSOLDIER),"SPAWN SOLDIER"
    print len(SPAWNZOMBIE),"SPAWN ZOMBIE"
    my_server = MyServer(localaddr = (sys.argv[1],int(sys.argv[2])))
    my_server.launch_game()
