#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
    Very simple game with Pygame
"""

import sys, pygame, math
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
global idShot
idShot = 0
maps = niveau.carte
vitesse = 5
vitesseDiag = math.sqrt((vitesse*vitesse)/2)
# Vitesse du zombie (Coefficient)
vitesseZombie = 1.1
zombieTues = 0
global manche
manche = 1
# Nombres de zombie nécéssaires à la manche 1
global coeffManche
coeffManche = 3


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
    try :
        return maps[int(y/20)][int(x/20)] == "#"
    except IndexError :
        return False


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
class Shot(pygame.sprite.Sprite):
    """Class for shot"""

    def __init__(self, id, x, y, orientation):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('Pics/shot/tir-e.png')
        self.orientation = orientation
        self.rect.x = x
        self.rect.y = y
        self.id = id

    def update(self):
        if self.orientation == 'nw':
            self.rect = self.rect.move([-vitesseDiag*2,-vitesseDiag*2])
        elif self.orientation == 'ne':
            self.rect = self.rect.move([vitesseDiag*2,-vitesseDiag*2])
        elif self.orientation == 'sw':
            self.rect = self.rect.move([-vitesseDiag*2,vitesseDiag*2])
        elif self.orientation == 'se':
            self.rect = self.rect.move([vitesseDiag*2,vitesseDiag*2])
        elif self.orientation == 'n':
            self.rect = self.rect.move([0,-vitesse*2])
        elif self.orientation == 's':
            self.rect = self.rect.move([0,vitesse*2])
        elif self.orientation == 'w':
            self.rect = self.rect.move([-vitesse*2,0])
        elif self.orientation == 'e':
            self.rect = self.rect.move([vitesse*2,0])

        if pygame.sprite.spritecollide(self, MAP, False):
            my_server.shots.remove(self)
            my_server.sendRemoveShots(self)

    def getId(self):
        return self.id

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
        self.image, self.rect = load_png('Pics/zombie.png')
        self.orientation = 'e'
        self.id = id
        self.angle = 0
        randspawn = randint(0,len(SPAWNZOMBIE)-1)
        self.rect.x = SPAWNZOMBIE[randspawn].getX()
        self.rect.y = SPAWNZOMBIE[randspawn].getY()

    def update(self, soldier):
        global manche

        vectDir = getVecteurDirecteur(Vec2d(self.rect.x,self.rect.y),Vec2d(soldier.getX(),soldier.getY()),3)

        if vectDir:
            self.angle = math.atan2(vectDir.x, vectDir.y)*180/math.pi
            self.rect.x += vectDir.x*((coeffManche*manche)/2)*vitesseZombie
            self.rect.y += vectDir.y*((coeffManche*manche)/2)*vitesseZombie


        rectx = self.rect.x
        recty = self.rect.y
        # Vérification de la position
        if pygame.sprite.spritecollide(self, MAP, False):
            #print '---COLLIDE---',self.rect.x,self.rect.y
            self.rect.x = rectx
            self.rect.y = recty

        shots_list = pygame.sprite.spritecollide(self, my_server.shots, True)
        if shots_list:
            my_server.zombies.remove(self)
            my_server.sendRemoveZombie(self)
            global zombieTues
            zombieTues += 1
            if zombieTues >= coeffManche*manche:
                manche += 1
                my_server.sendManche()
                zombieTues = 0
            for shot in shots_list:
                my_server.shots.remove(shot)
                my_server.sendRemoveShots(shot)

    def getId(self):
        return self.id



class Soldier(pygame.sprite.Sprite):
    """Class for the player"""

    def __init__(self, number):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('Pics/survivor2/survivor_e.png')
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
            self.rect = self.rect.move([-vitesseDiag,-vitesseDiag])
        elif keys[K_UP] and keys[K_RIGHT]:
            self.orientation = 'ne'
            self.rect = self.rect.move([vitesseDiag,-vitesseDiag])
        elif keys[K_DOWN] and keys[K_LEFT]:
            self.orientation = 'sw'
            self.rect = self.rect.move([-vitesseDiag,vitesseDiag])
        elif keys[K_DOWN] and keys[K_RIGHT]:
            self.orientation = 'se'
            self.rect = self.rect.move([vitesseDiag,vitesseDiag])
        elif keys[K_UP]:
            self.orientation = 'n'
            self.rect = self.rect.move([0,-vitesse])
        elif keys[K_DOWN]:
            self.orientation = 's'
            self.rect = self.rect.move([0,vitesse])
        elif keys[K_LEFT]:
            self.orientation = 'w'
            self.rect = self.rect.move([-vitesse,0])
        elif keys[K_RIGHT]:
            self.orientation = 'e'
            self.rect = self.rect.move([vitesse,0])

        global idShot

        if keys[K_SPACE]:
            shot = Shot(idShot, self.rect.x,self.rect.y,self.orientation)
            my_server.shots.add(shot)
            for client in my_server.clients:
                message = [ shot.rect.x, shot.rect.y, shot.orientation ]
                client.Send({'action':'shots','id':shot.getId(),'message':message})
            idShot += 1

        # Vérification de la position
        if pygame.sprite.spritecollide(self, MAP, False):
            #print '---COLLIDE---',self.rect.x,self.rect.y
            self.rect.x = rectx
            self.rect.y = recty

        if pygame.sprite.spritecollide(self, my_server.zombies, False):
            for client in my_server.clients:
                client.Send({'action':'end'})



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
        self.idZombie = 0
        pygame.init()
        self.screen = pygame.display.set_mode((128, 128))
        print('Server launched')

    def nouveauZombie(self):
        # On choisi un lieu de spawn parmi ceux qui existe
        randspawn = randint(0,len(SPAWNZOMBIE)-1)

        nouveau_zombie = Zombie(randspawn, self.idZombie)
        self.idZombie += 1
        self.zombies.append(nouveau_zombie)
        # On envoi le nouveau zombie a chaque client
        for client in self.clients:
                message = [ nouveau_zombie.rect.x, nouveau_zombie.rect.y, nouveau_zombie.orientation, nouveau_zombie.angle ]
                client.Send({'action':'zombie','id':nouveau_zombie.getId(),'message':message})

    def Connected(self, channel, addr):
        self.clients.append(channel)
        channel.create_soldier(len(self.clients))
        print('New connection: %d client(s) connected' % len(self.clients))

        if len(self.clients) == 2:
            for client in self.clients:
                client.Send({'action':'start'})

            self.zombies = []
            self.shots = pygame.sprite.RenderClear()

            for i in range(0,2):
                randspawn = randint(0,len(SPAWNZOMBIE)-1)
                nouveau_zombie = Zombie(randspawn, len(self.zombies))
                self.zombies.append(nouveau_zombie)

            for client in self.clients:
                global manche
                client.Send({'action':'manche','message':manche})
                for zombie in self.zombies:
                    message = [ zombie.rect.x, zombie.rect.y, zombie.orientation, zombie.angle ]
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
        message1 = [ soldier1.rect.x, soldier1.rect.y, soldier1.orientation ]
        message2 = [ soldier2.rect.x, soldier2.rect.y, soldier2.orientation ]
        for client in self.clients:
            client.Send({'action':'soldier', 'soldier1':message1, 'soldier2':message2})

    def send_zombies(self):
        for client in self.clients:
            for zombie in self.zombies:
                message = [ zombie.rect.x, zombie.rect.y, zombie.orientation, zombie.angle ]
                client.Send({'action':'zombieMouvements','id':zombie.getId(),'message':message})

    def send_shots(self):
        for client in self.clients:
            for shot in self.shots:
                message = [ shot.rect.x, shot.rect.y, shot.orientation ]
                client.Send({'action':'shotsMouvements','id':shot.getId(),'message':message})

    def sendRemoveZombie(self, zombie):
        for client in self.clients:
            client.Send({'action':'removeZombie','id':zombie.getId()})

    def sendRemoveShots(self, shot):
        for client in self.clients:
            client.Send({'action':'removeShot','id':shot.getId()})

    def sendManche(self):
        for client in self.clients:
            global manche
            client.Send({'action':'manche','message':manche})

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
        temps = time.time()

        while True:
            clock.tick(60)
            self.Pump()

            if self.run:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quitter()

                diff = time.time() - temps
                # On crée un nouveau zombie toutes les 10 secondes
                if (time.time() - temps) > 10 :
                    my_server.nouveauZombie()
                    temps = time.time()

                # updates des différents zombies
                for zombie in self.zombies:
                    # On regarde lequel des deux soldats est le plus prêt du zombie
                    if math.sqrt((self.clients[0].soldier.rect.x - zombie.rect.x)**2 + (self.clients[0].soldier.rect.y - zombie.rect.y)**2) > math.sqrt((self.clients[1].soldier.rect.x - zombie.rect.x)**2 + (self.clients[1].soldier.rect.y - zombie.rect.y)**2):
                        zombie.update(self.clients[1].soldier)
                    else:
                        zombie.update(self.clients[0].soldier)

                # updates des tirs
                for shot in self.shots:
                    shot.update()
                self.send_soldiers()
                self.send_zombies()
                self.send_shots()

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

    # Lecture du fichier contenant les informations de la MAP (Lieux d'apparition, murs)
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
                #print '--ADD SPAWN SOLDIER--',x,':',y,'rect',spawn.rect
            elif char == "Z":
                spawn = SpawnZombie(x,y)
                SPAWNZOMBIE.append(spawn)
                #print '--ADD SPAWN ZOMBIE--',x,':',y,'rect',spawn.rect
            x+=20
        y+=20

    print len(MAP),"BLOCK SPAWNED"
    print len(SPAWNSOLDIER),"SPAWN SOLDIER"
    print len(SPAWNZOMBIE),"SPAWN ZOMBIE"
    my_server = MyServer(localaddr = (sys.argv[1],int(sys.argv[2])))
    my_server.launch_game()
