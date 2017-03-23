#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
    Dark Destination
"""
import sys, pygame
import signal
import os
import time
from pygame.locals import *
import random
from PodSixNet.Connection import connection, ConnectionListener
pygame.font.init()
font = pygame.font.Font("Font/zombnze.ttf", 60)
manche = 0

finDePartie = False

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
class Shot(pygame.sprite.Sprite, ConnectionListener):
    """Class for shot"""

    def __init__(self, id, x, y, orientation):
        pygame.sprite.Sprite.__init__(self)
        # sound = pygame.mixer.Sound("Sounds/shotSound.wav")
        # sound.play()
        self.orientation = orientation
        if self.orientation == 'n':
            self.image, self.rect = load_png("Pics/shot/tir-n.png")
        elif self.orientation == 's':
            self.image, self.rect = load_png("Pics/shot/tir-s.png")
        elif self.orientation == 'w':
            self.image, self.rect = load_png("Pics/shot/tir-w.png")
        elif self.orientation == 'e':
            self.image, self.rect = load_png("Pics/shot/tir-e.png")
        elif self.orientation == 'ne':
            self.image, self.rect = load_png("Pics/shot/tir-ne.png")
        elif self.orientation == 'nw':
            self.image, self.rect = load_png("Pics/shot/tir-nw.png")
        elif self.orientation == 'se':
            self.image, self.rect = load_png("Pics/shot/tir-se.png")
        elif self.orientation == 'sw':
            self.image, self.rect = load_png("Pics/shot/tir-sw.png")
        self.rect.centerx = x
        self.rect.y = y
        self.id = id

    def update(self, x, y, orientation):
        self.rect.centerx = x
        self.rect.y = y
        self.orientation = orientation

    def getImage(self):
        return self.image

    def getX(self):
        return self.rect.centerx

    def getY(self):
        return self.rect.y

    def getId(self):
        return self.id

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

    def Network_manche(self, data):
        global manche
        manche = data['message']

    def Network_end(self, data):
        game_client.run = False
        global finDePartie
        finDePartie = True

    def Network_disconnected(self, data):
        print('Server disconnected')
        quitter()

class Zombie(pygame.sprite.Sprite):
    """Class for the zombie"""

    def __init__(self, id, x, y, orientation, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('Pics/zombie.png')
        self.orientation = orientation
        self.angle = angle
        self.rect.centerx = x
        self.rect.y = y
        self.id = id

    def update(self, x, y, orientation, angle):
        self.rect.centerx = x
        self.rect.y = y
        self.orientation = orientation
        self.angle = angle

    def getImage(self):
        return self.image

    def getX(self):
        return self.rect.centerx

    def getY(self):
        return self.rect.y

    def getId(self):
        return self.id


# CLASSES
class ShotsGroups(pygame.sprite.Sprite, ConnectionListener):
    """Class for the zombie groups"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.shotsSprite = pygame.sprite.RenderClear()

    def Network_shots(self,data):
        nouveauShot = Shot(data['id'],data['message'][0],data['message'][1],data['message'][2])
        self.shotsSprite.add(nouveauShot)

    def Network_shotsMouvements(self,data):
        for shot in self.shotsSprite:
            # On cherche le bon shot parmi tous les shots
            if shot.getId()==data['id']:
                shot.update(data['message'][0],data['message'][1],data['message'][2])

    def Network_removeShot(self,data):
        for shot in self.shotsSprite:
            if shot.getId()==data['id']:
                self.shotsSprite.remove(shot)

    def update(self):
        self.Pump()

class ZombieGroups(pygame.sprite.Sprite, ConnectionListener):
    """Class for the zombie groups"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.zombiesSprite = pygame.sprite.RenderClear()

    def Network_zombie(self,data):
        nouveauZombie = Zombie(data['id'],data['message'][0],data['message'][1],data['message'][2],data['message'][3])
        self.zombiesSprite.add(nouveauZombie)

    def Network_zombieMouvements(self,data):
        for zombie in self.zombiesSprite:
            if zombie.getId()==data['id']:
                zombie.update(data['message'][0],data['message'][1],data['message'][2],data['message'][3])

    def Network_removeZombie(self,data):
        for zombie in self.zombiesSprite:
            if zombie.getId()==data['id']:
                self.zombiesSprite.remove(zombie)

    def update(self):
        self.Pump()

class Soldier(pygame.sprite.Sprite, ConnectionListener):
    """Class for the player"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('Pics/survivor1/survivor_e.png')
        self.image_n,_ = load_png("Pics/survivor1/survivor_n.png")
        self.image_s,_ = load_png("Pics/survivor1/survivor_s.png")
        self.image_w,_ = load_png("Pics/survivor1/survivor_w.png")
        self.image_e,_ = load_png("Pics/survivor1/survivor_e.png")
        self.image_n_e,_ = load_png("Pics/survivor1/survivor_n_e.png")
        self.image_s_e,_ = load_png("Pics/survivor1/survivor_s_e.png")
        self.image_n_w,_ = load_png("Pics/survivor1/survivor_n_w.png")
        self.image_s_w,_ = load_png("Pics/survivor1/survivor_s_w.png")
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

    def getX(self):
        return self.rect.centerx

    def getY(self):
        return self.rect.y

    def getImage(self):
        return self.image

    def getRect(self):
        return self.rect


class Soldier2(pygame.sprite.Sprite, ConnectionListener):
    """Class for the player"""

    def __init__(self):
    	pygame.sprite.Sprite.__init__(self)
    	self.image,self.rect=load_png("Pics/survivor2/survivor_n.png")
    	self.image_n,_ = load_png("Pics/survivor2/survivor_n.png")
    	self.image_s,_ = load_png("Pics/survivor2/survivor_s.png")
    	self.image_w,_ = load_png("Pics/survivor2/survivor_w.png")
    	self.image_e,_ = load_png("Pics/survivor2/survivor_e.png")
        self.image_n_e,_ = load_png("Pics/survivor2/survivor_n_e.png")
        self.image_s_e,_ = load_png("Pics/survivor2/survivor_s_e.png")
        self.image_n_w,_ = load_png("Pics/survivor2/survivor_n_w.png")
        self.image_s_w,_ = load_png("Pics/survivor2/survivor_s_w.png")
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
        elif self.orientation == 'ne':
            self.image = self.image_n_e
        elif self.orientation == 'nw':
            self.image = self.image_n_w
        elif self.orientation == 'se':
            self.image = self.image_s_e
        elif self.orientation == 'sw':
            self.image = self.image_s_w
        self.rect.center = data['soldier2'][0:2]

    def update(self):
        self.Pump()

    def getX(self):
        return self.rect.centerx

    def getY(self):
        return self.rect.y

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
    # pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.key.set_repeat(1,1)

    # Elements
    background_image, background_rect = load_png('Pics/map.png')
    background_image = pygame.transform.scale(background_image, (background_rect.width*2,background_rect.height*2))

    wait_image, wait_rect = load_png('Pics/wait1.png')
    wait_rect.center = [ SCREEN_WIDTH/2, SCREEN_HEIGHT/2 ]
    screen.blit(background_image, background_rect)


    soldier_sprite = pygame.sprite.RenderClear()
    zombie_sprite = ZombieGroups()
    shots_sprite = ShotsGroups()

    soldier1 = Soldier()
    soldier2 = Soldier2()

    soldier_sprite.add(soldier1)
    soldier_sprite.add(soldier2)

    player1 = False
    cameraX = 0
    cameraY = 0

    while True:
        clock.tick(120)
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
            zombie_sprite.update()
            shots_sprite.update()

            # drawings

            screen.fill((0,0,0))

            #Calculer offset camera
            cameraX = (soldier1.getX() if player1 else soldier2.getX())-(SCREEN_WIDTH/2)
            cameraY = (soldier1.getY() if player1 else soldier2.getY())-(SCREEN_HEIGHT/2)

            # background_rect = background_rect.move([10,10])
            screen.blit(background_image, (-cameraX, -cameraY))



            for soldier in soldier_sprite:
                screen.blit(soldier.getImage(),(soldier.getX()-cameraX+(soldier.rect.width/2), soldier.getY()-cameraY+(soldier.rect.height/2)))

            for zombie in zombie_sprite.zombiesSprite:
                screen.blit(pygame.transform.rotate(zombie.image, zombie.angle), (zombie.getX()-cameraX,zombie.getY()-cameraY))

            for shot in shots_sprite.shotsSprite:
                screen.blit(shot.getImage(), (shot.getX()-cameraX+50,shot.getY()-cameraY+50))

            textImg = font.render("Manche : "+str(manche), 1, (153,0,0))
            screen.blit( textImg, (0,0) )

            # soldier_sprite.clear(screen, background_image)
            # soldier_sprite.draw(screen)

        else: # game is not running
            if not finDePartie :
                screen.blit(wait_image, wait_rect)
                player1 = True
            else :
                text1 = font.render("Fin de partie", 1, (153,0,0))
                text2 = font.render("Vous avez atteint la manche : "+str(manche), 1, (153,0,0))
                screen.blit( text1, (3*font.get_linesize(),3*font.get_linesize()) )
                screen.blit( text2, (3*font.get_linesize(),4*font.get_linesize()) )

        pygame.display.flip()
