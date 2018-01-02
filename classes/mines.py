import math
from functions import images as im
import pygame
from functions import mapp as m
from functions import sounds
from random import randint


class Mine():

    def __init__(self, Pos):
        self.xPos = Pos[0]
        self.yPos = Pos[1]
        self.width = Pos[2]
        self.height = Pos[3]
        self.timeToLive = 50
        self.isDead = False
        self.frame = 10
        self.img = im.get_image("data/img/gravitymine.png")
        self.imgState = 0
        self.explosionFrame = 0
        self.damage = 90
        self.hasPlayedSound = False
        self.deathSound = sounds.get_sound("data/sound/sfx/mineimplosion.wav")
        self.volume = 0.1

        self.hasStaticVolume = False

        self.r = ((self.width + self.height) / 2) / 2
    
    def get_volume(self, svol, cam):
        if not self.hasStaticVolume:
            mpbnds = m.get_map_bounds()
            avebnd = mpbnds[0] / 2 + mpbnds[1] / 2

            distFromCam = abs(math.hypot(cam[0] - self.xPos, cam[1] - self.yPos))

            svol = svol * ((avebnd - distFromCam) / (avebnd * 10))

            return svol
        
        else:
            return svol / 100

    def show(self, screen, cam):
        self.deathSound.set_volume(self.volume)
        self.frame -= 1
        if self.isDead and not self.hasPlayedSound:
            self.hasPlayedSound = True
            self.deathSound.play()

        if self.frame == 0:
            if self.imgState == 0:
                self.img = im.get_image("data/img/gravitymine2.png")
                self.imgState = 1
            else:
                self.img = im.get_image("data/img/gravitymine.png")
                self.imgState = 0
            
            self.frame = 10
        
        if not self.isDead:
            self.nimg = pygame.transform.scale(self.img, (self.width, self.height))
            playerImg = (self.nimg, (self.xPos - cam[0] - self.width / 2, self.yPos - cam[1] - self.height / 2))
            screen.blit(playerImg[0], playerImg[1])

        else:
            
            if self.explosionFrame <= 11:
                self.explosionFrame += 1

                explImg = im.get_image("data/img/purpleexplosion/" + str(self.explosionFrame) + ".png")
                explImg = pygame.transform.scale(explImg, (self.width, self.height))
                screen.blit(explImg, (self.xPos - cam[0] - self.width / 2, self.yPos - cam[1] - self.height / 2))
                

    
    def isTouchingCircle(self, Pos, r):

        dist = math.hypot(self.xPos - Pos[0], self.yPos - Pos[1])

        if dist <= abs(r / 2) + abs(self.r / 2):
            return True
        return False

class Upgrade():

    def __init__(self, Pos, isMarker=False, markerText="", canBePickedUp=True):
        self.xPos = Pos[0]
        self.yPos = Pos[1]
        self.width = Pos[2]
        self.height = Pos[3]
        self.timeToLive = 50
        self.isDead = False
        self.frame = 10
        if not isMarker:
            self.img = im.get_image("data/img/upgradetoken.png")
        self.imgState = 0
        self.explosionFrame = 0
        self.hasPlayedSound = False
        self.deathSound = sounds.get_sound("data/sound/sfx/upgrade.wav")
        self.volume = 0.1
        self.isMarker = isMarker
        self.markerFrame = 0
        self.markerTickDir = 1
        self.markerText = markerText.split("\n")
        self.canBePickedUp = canBePickedUp
        self.font = pygame.font.Font("data/font/PressStart2P.ttf", 15)

        self.hasStaticVolume = False
        self.r = ((self.width + self.height) / 2) / 2

    def get_volume(self, svol, cam):
        if not self.hasStaticVolume:
            mpbnds = m.get_map_bounds()
            avebnd = mpbnds[0] / 2 + mpbnds[1] / 2

            distFromCam = abs(math.hypot(cam[0] - self.xPos, cam[1] - self.yPos))

            svol = svol * ((avebnd - distFromCam) / (avebnd * 18))

            return svol

        else:
            return svol / 100
        
    def show(self, screen, cam):
        #print(self.frame)
        self.deathSound.set_volume(self.volume)
        self.frame -= 1
        if self.isDead and not self.hasPlayedSound:
            self.hasPlayedSound = True
            self.deathSound.play()
            self.frame = 10
        
        if not self.isDead:
            if not self.isMarker:
                self.nimg = pygame.transform.scale(self.img, (self.width, self.height))
                playerImg = (self.nimg, (self.xPos - cam[0] - self.width / 2, self.yPos - cam[1] - self.height / 2))
                screen.blit(playerImg[0], playerImg[1])

            else:
                self.nimg = pygame.transform.scale(im.get_image("data/img/movehere/" + str(self.markerFrame) + ".png"), (self.width, self.height))
                playerImg = (self.nimg, (self.xPos - cam[0] - self.width / 2, self.yPos - cam[1] - self.height / 2))
                screen.blit(playerImg[0], playerImg[1])

                if self.markerFrame >= 3 and self.markerTickDir == 1:
                    self.markerTickDir = -1
                elif self.markerFrame <= 0 and self.markerTickDir == -1:
                    self.markerTickDir = 1

                if self.frame % 4 == 0:
                    self.markerFrame += self.markerTickDir
                
                for i in range(0, len(self.markerText)):
                    text = self.font.render(self.markerText[i], True, (180, 180, 180))
                    screen.blit(text, (self.xPos - cam[0] - text.get_width() / 2, self.yPos - cam[1] + text.get_height() * i + 30))
        else:
            
            if self.explosionFrame < 6:
                self.explosionFrame += 1

                explImg = im.get_image("data/img/upgrade/upgrade" + str(self.explosionFrame) + ".png")
                explImg = pygame.transform.scale(explImg, (self.width, self.height))
                screen.blit(explImg, (self.xPos - cam[0] - self.width / 2, self.yPos - cam[1] - self.height / 2))
    def isTouchingCircle(self, Pos, r):

        dist = math.hypot(self.xPos - Pos[0], self.yPos - Pos[1])

        if dist <= abs(r / 2) + abs(self.r / 2):
            return True
        return False