import math
from functions import images
import pygame
from functions import fonts
from functions import mapp as m
from random import randint
from functions import sounds
from functions import ubers as ub

class Dust():

    def __init__(self, Pos):
        self.xPos = Pos[0]
        self.yPos = Pos[1]
        self.width = Pos[2]
        self.height = Pos[3]
        self.lifetime = 300
        self.img = images.get_image("data/img/dust/" + str(randint(0, 2)) + ".png")
        self.ang = randint(0, 360)

    def show(self, screen, cam):
        if self.lifetime > 0:
            self.lifetime -= 1

        self.nimg = pygame.transform.scale(self.img, (self.width, self.height))
        ocenter = self.nimg.get_rect().center
        self.nimg = pygame.transform.rotate(self.nimg, self.ang)
        rect = self.nimg.get_rect()
        rect.center = ocenter

        bulletImg = (self.nimg, (self.xPos - (rect.width / 2) - cam[0], self.yPos - (rect.height / 2) - cam[1]))
        screen.blit(bulletImg[0], bulletImg[1])

class Bullet():

    def __init__(self, Pos, ang, vel, isball=False, ismissile=False, maxLifetime=100, isMelee=False, isPentagram=False):
        self.xPos = Pos[0]
        self.yPos = Pos[1]
        self.width = Pos[2]
        self.height = Pos[3]
        self.vel = vel
        self.ang = ang
        self.lifetime = 0
        self.ismissile = ismissile
        self.maxLifetime = maxLifetime
        self.r = (self.width + self.height) / 2 / 2 + 10
        self.img = images.get_image('data/img/laser.png')
        self.damage = 16
        self.isball = isball
        self.isnyancat1 = False
        self.isMelee = isMelee
        self.isPentagram = isPentagram
        if self.isball:
            self.img = images.get_image('data/img/ball.png')
            self.damage = 60
        elif self.ismissile:
            self.img = images.get_image('data/img/nyancat.png')
            self.isnyancat1 = True
        elif self.isMelee:
            self.img = images.get_image('data/img/melee.png')
            self.damage = 25
        elif self.isPentagram:
            self.img = images.get_image("data/img/pentagram.png")
            self.damage = 10

        #print(self.r)

    def get_velocity(self):
        xvel = self.vel * math.cos((self.ang + 90) * (math.pi / 180))
        yvel = -self.vel * math.sin((self.ang + 90) * (math.pi / 180))

        return (xvel, yvel)

    def tick(self, mapDims, shouldLoop=False):
        
        self.lifetime += 1

        if not self.isMelee:

            trueVel = self.get_velocity()
            self.xPos += trueVel[0]
            self.yPos += trueVel[1]

            if self.lifetime % 18 == 0:
                self.damage -= 1
            
            if self.lifetime % 3 == 0:
                if self.ismissile:
                    if self.isnyancat1:
                        self.img = images.get_image('data/img/nyancat2.png')
                        self.isnyancat1 = False
                    else:
                        self.img = images.get_image('data/img/nyancat1.png')
                        self.isnyancat1 = True

            if self.xPos > mapDims[0]:
                if shouldLoop:
                    self.xPos = 0
                    self.maxLifetime -= 75
            if self.yPos > mapDims[1]:
                if shouldLoop:
                    self.yPos = 0
                    self.maxLifetime -= 75
            if self.xPos < 0: 
                if shouldLoop:
                    self.xPos = mapDims[0]
                    self.maxLifetime -= 75
            if self.yPos < 0: 
                if shouldLoop:
                    self.yPos = mapDims[1]
                    self.maxLifetime -= 75

        if self.lifetime > self.maxLifetime:
            return False
        else:
            return True

    def isTouchingCircle(self, Pos, r):

        dist = math.hypot(self.xPos - Pos[0], self.yPos - Pos[1])

        if dist <= abs(r / 2) + abs(self.r / 2):
            return True
        return False

    def show(self, screen, cam):


        self.nimg = pygame.transform.scale(self.img, (self.width, self.height))
        ocenter = self.nimg.get_rect().center
        self.nimg = pygame.transform.rotate(self.nimg, self.ang)
        rect = self.nimg.get_rect()
        rect.center = ocenter

        bulletImg = (self.nimg, (self.xPos - (rect.width / 2) - cam[0], self.yPos - (rect.height / 2) - cam[1]))
        screen.blit(bulletImg[0], bulletImg[1])


class Player():

    img = images.get_image('data/img/player.png')
    redimg = images.get_image('data/img/redplayer.png')
    grnimg = images.get_image('data/img/grnplayer.png')
    ylwimg = images.get_image('data/img/ylwplayer.png')

    def __init__(self, Pos, ang, vel, teamnum, playerNum, hea, isAi=False, isCreep=False):

        self.lives = 0

        self.fireSound = sounds.get_sound("data/sound/sfx/mainlaser.wav")
        if isCreep:
            self.fireSound = sounds.get_sound("data/sound/sfx/creephit.wav")
        self.explosionFrame = -1
        self.isDead = False
        self.xPos = Pos[0]
        self.yPos = Pos[1]
        self.width = Pos[2]
        self.height = Pos[3]
        self.ang = ang
        self.vel = vel
        self.teamnum = int(teamnum)
        self.turnVel = 0
        self.isAi = isAi
        self.hitsound = sounds.get_sound("data/sound/sfx/playerhit.wav")

        if not self.isAi:
            self.headTurningSharpness = 7.9
        else:
            self.headTurningSharpness = 11
        if not self.isAi:
            self.headTurningLatency = .75
        else:
            self.headTurningLatency = .35
        self.timeToRespawn = -1
        self.bullets = []
        self.timeToFire = 25
        self.timeToDoubleShot = -1
        self.hea = hea
        self.maxhea = hea
        self.r = (self.width + self.height) / 2 / 2 + 10
        self.pnum = playerNum
        self.teamcolor = (200, 200, 200, 80)

        mpbnds = m.get_map_bounds()
        self.target = (mpbnds[0] / 2, mpbnds[1] / 2)
        self.isTargetingPlayer = False
        if self.teamnum == 1:
            self.realImg = self.img
            self.teamcolor = (160, 160, 255, 80)
        elif self.teamnum == 2:
            self.realImg = self.redimg
            self.teamcolor = (250, 160, 160, 80)
        elif self.teamnum == 3:
            self.realImg = self.grnimg
            self.teamcolor = (160, 250, 160, 80)
        elif self.teamnum == 4:
            self.realImg = self.ylwimg
            self.teamcolor = (220, 250, 100, 80)
        else:
            self.realImg = self.img

        self.hasExploded = False
        self.lframe = 0
        self.volume = 0.01
        self.deathSound = sounds.get_sound("data/sound/sfx/explosion" + str(randint(1, 2)) + ".wav")

        self.UBERtype = ub.get_random_uber()["type"]
        self.hasUBER = False
        self.UBERiconimg = images.get_image("data/img/ylwarrow.png")

        self.isSpeedDemon = 0
        self.isInvincible = True
        self.shieldTimer = 1

        self.hearegen = 0
        self.didHaveUBER = False
        self.hasSwappedUberBuffer = 0
        
        self.hasStaticVolume = False
        self.gametype = "standard"

        self.isSacrificingBlood = False
        self.isSacBloodBuffer = 0
        self.currentBloodAuraImg = 1
        self.bloodAuraImg = images.get_image("data/img/bloodaura/" + str(self.currentBloodAuraImg) + ".png")
        self.flameCircleR = self.r

        self.isDashing = False
        self.dashBuffer = 0
        self.dashCooldown = 0
        self.dashTurnDir = "right"

        self.shouldShowDashFlash = False
        self.dashFlashFrame = 0
        self.dashFlashPos = (self.xPos, self.yPos)
        self.dashFlashImg = images.get_image("data/img/flash/" + str(self.dashFlashFrame) + ".png")
        self.dashFlashSound = sounds.get_sound("data/sound/sfx/flashdash.wav")
        self.dashFlashCooldownImg = images.get_image("data/img/flashcd.png")

        self.mpbnds = m.get_map_bounds()
        self.aiType = ""
        self.isCreep = isCreep
        self.creepFrame = 0
        if self.isCreep:
            self.lives = 0
            self.realImg = images.get_image("data/img/creep/" + str(self.creepFrame) + ".png")
        #print(str(self.pnum) + " " + str(self.teamnum))
        
        self.dustConnectionLeniency = 95
        self.dustMinCircleyness = 1.95
        self.minAmtOfDustPlaced = 8
        self.dust = []
        

    def playhitsound(self):
        self.hitsound.set_volume(self.volume)
        self.hitsound.play()

    def get_volume(self, svol, cam):
        if not self.hasStaticVolume:
            avebnd = self.mpbnds[0] / 2 + self.mpbnds[1] / 2

            distFromCam = abs(math.hypot(cam[0] - self.xPos, cam[1] - self.yPos))

            svol = svol * ((avebnd - distFromCam) / (avebnd * 22))

            return svol

        else:
            return svol / 100

    def get_team_color(self):
        return self.teamcolor

    def isTouchingCircle(self, Pos, r):

        dist = math.hypot(self.xPos - Pos[0], self.yPos - Pos[1])

        if dist <= abs(r / 2) + abs(self.r / 2):
            return True
        return False

    def checkIfDying(self):
        self.nisDead = False
        if self.hea <= 0:
            self.nisDead = True
            self.hea = 0

        if self.nisDead == True and self.isDead == False:
            self.isSacrificingBlood = 0
            return True

        return False

    def isTouchingFlame(self, Pos, r):
        if self.UBERtype == "blood4flame" and self.isSacrificingBlood == True:
            dist = math.hypot(self.xPos - Pos[0], self.yPos - Pos[1])
            #print(str(dist))
            if dist <= abs(r / 2) + abs(self.flameCircleR / 2):
                return True
            return False

    def tick(self, mapDims, teamlives, screenDims):
        if self.isSacBloodBuffer > 0:
            self.isSacBloodBuffer -= 1

        ## efficiency ## width ## height ## variable storage
        self.owidth = self.width
        self.oheight = self.height
        self.oang = self.ang

        #print (self.isSacrificingBlood)
        if self.isCreep:
            if self.lframe % 3 == 0:
                self.creepFrame += 1
                if self.creepFrame > 3:
                    self.creepFrame = 0
                self.hasUBER = False
            self.realImg = images.get_image("data/img/creep/" + str(self.creepFrame) + ".png")

        if self.isSacrificingBlood:
            self.hea -= 1.05
            if self.UBERtype == "blood4bullets":
                if self.lframe % 15 == 0:
                    for i in range(0, randint(4, 9)):
                        tbullet = Bullet((self.xPos, self.yPos, 12, 48), self.ang + randint(-40, 40), 20)
                        tbullet.damage *= 1.2
                        tbullet.lifetime = 84
                        self.bullets.append(tbullet)
                self.hea -= 0.15
            
            elif self.UBERtype == "blood4flame":
                self.isInvincible = True
                self.flameCircleR += 1.1
                if self.flameCircleR > self.r * 2:
                    self.flameCircleR = self.r

                self.hea += 0.45

            elif self.UBERtype == "blood4dust":
                self.hea += 0.6
                if self.lframe % 4 == 0:
                    self.dust.append(Dust((self.xPos, self.yPos, 40, 40)))

        for dust in self.dust:
            if dust.lifetime == 0:
                self.dust.remove(dust)

        if len(self.dust) >= self.minAmtOfDustPlaced and self.lframe % 5 == 0:
            dst1 = self.dust[len(self.dust) - 1]
            dst2 = self.dust[0]
            if math.hypot(dst1.xPos - dst2.xPos, dst1.yPos - dst2.yPos) < self.dustConnectionLeniency:
                heighestXPos = {"x": 0, "y": 0}
                heighestYPos = {"x": 0, "y": 0}
                lowestXPos = {"x": 0, "y": 0}
                lowestYPos = {"x": 0, "y": 0}

                ## get most extreme points for each direction/axis ## dust ## create dust
                for i in range(0, len(self.dust)):
                    dust = self.dust[i]
                    if dust.xPos > heighestXPos["x"] or i == 0:
                        heighestXPos["x"] = dust.xPos
                        heighestXPos["y"] = dust.yPos
                    if dust.yPos > heighestYPos["y"] or i == 0:
                        heighestYPos["x"] = dust.xPos
                        heighestYPos["y"] = dust.yPos
                    if dust.xPos < lowestXPos["x"] or i == 0:
                        lowestXPos["x"] = dust.xPos
                        lowestYPos["y"] = dust.yPos
                    if dust.yPos < lowestYPos["y"] or i == 0:
                        lowestYPos["x"] = dust.xPos
                        lowestYPos["y"] = dust.yPos
                    
                rightLeftLength = math.hypot(heighestXPos["x"] - lowestXPos["x"], heighestXPos["y"] - lowestXPos["y"])
                topBotLength = math.hypot(heighestYPos["x"] - lowestYPos["x"], heighestYPos["y"] - lowestYPos["y"])
                fract = 0
                if rightLeftLength > topBotLength:
                    fract = rightLeftLength / topBotLength
                else:
                    fract = topBotLength / rightLeftLength
                
                if fract < self.dustMinCircleyness: ## note: circleyness of fract just approaches 1 as it becomes a perfect "circle"
                    middleX = int((heighestXPos["x"] + lowestXPos["x"] + heighestYPos["x"] + lowestYPos["x"]) / 4)
                    middleY = int((heighestXPos["y"] + lowestXPos["y"] + heighestYPos["y"] + lowestYPos["y"]) / 4)
                    aveLength = int((rightLeftLength + topBotLength) / 2)

                    meleeBullet = Bullet((middleX, middleY, aveLength, aveLength), 0, 0, isPentagram=True, maxLifetime=50)
                    self.bullets.append(meleeBullet)
                    self.dust = []


        if self.dashBuffer > 0:
            self.dashBuffer -= 1
        if self.dashCooldown > 0:
            self.dashCooldown -= 1

        if self.UBERtype != "blood4flame" and self.shieldTimer <= 0:
            self.isInvincible = False
                
        if self.UBERtype[:6] != "blood4" and self.isSacBloodBuffer == 0:
            self.isSacrificingBlood = False


        if self.lframe % 2 == 0 and self.isSacrificingBlood:
            self.currentBloodAuraImg += 1
            if self.currentBloodAuraImg > 4:
                self.currentBloodAuraImg = 1

            self.bloodAuraImg = images.get_image("data/img/bloodaura/" + str(self.currentBloodAuraImg) + ".png")

        if self.lframe <= 2:
            m.mapBounds = [mapDims[0], mapDims[1]]

        if self.hasSwappedUberBuffer > 0:
            self.hasSwappedUberBuffer -= 1

        self.lframe += 1
        if self.lframe > 100000:
            self.lframe = 0
        
        if self.shieldTimer > 0:
            self.shieldTimer -= 1

        if self.shieldTimer == 0:
            self.isInvincible = False
        else:
            self.isInvincible = True

        self.hea += self.hearegen
        if self.isSpeedDemon > 0:
            self.isSpeedDemon -= 1

        
        # missile
        for bullet in self.bullets:
            if bullet.ismissile == True:
                if bullet.lifetime >= bullet.maxLifetime - 1:
                    for i in range(0, 16):
                        tbullet = Bullet((bullet.xPos, bullet.yPos, 12, 48), bullet.ang + randint(-50, 50), 20)
                        self.bullets.append(tbullet)
                    bullet.ismissile = False

        if self.hasUBER != self.didHaveUBER:
            self.UBERiconimg = images.get_image("data/img/ubers/"+self.UBERtype+".png")


        self.deathSound.set_volume(self.volume)

        if not self.isCreep:
            self.lives = teamlives[str(self.teamnum)]
        else:
            self.lives = 0

        self.ang += self.turnVel
        self.turnVel *= self.headTurningLatency

        self.txvel = self.vel * math.cos((self.ang + 90) * (math.pi / 180))
        self.tyvel = -self.vel * math.sin((self.ang + 90) * (math.pi / 180))
        
        self.xPos += self.txvel
        self.yPos += self.tyvel

        if self.hea > self.maxhea: self.hea = self.maxhea

        self.vel *= .98

        while len(self.bullets) > 70: 
            self.bullets.pop()

        if self.timeToFire > 0: 
            self.timeToFire -= 1
        if self.timeToDoubleShot > 0:
            self.timeToDoubleShot -= 1
        
        if not self.isCreep:
            if self.timeToDoubleShot == 0:
                self.timeToDoubleShot = -1
                barrelPos = self.getShiftedPos(-self.width / 5, 0)
                self.bullets.append(Bullet((self.xPos + barrelPos[0], self.yPos + barrelPos[1], 12, 48), self.ang, 20))

        try:
            for j in range(0, len(self.bullets)):
                j = len(self.bullets) - (j + 1)
                shouldLooop = (self.gametype == "arena")
                if not self.bullets[j].tick(mapDims, shouldLoop=shouldLooop):
                    self.bullets.pop(j)
        except:
            pass

        if self.isDead:
            if self.isCreep:
                self.lives = -1
            self.isSacrificingBlood = 0

            ## RESPAWN HERE BTW FUTURE ME ##
            if (self.hea == 180 or self.timeToRespawn == 200) and self.lives >= 0: # respawn

                self.hasUBER = False
                self.hearegen = 0
                self.deathSound = sounds.get_sound("data/sound/sfx/explosion" + str(randint(1, 2)) + ".wav")
                self.hea = self.maxhea

                if not self.isAi or self.gametype == "arena":
                    self.xPos = randint(0, int(screenDims[0] * .75))
                    self.yPos = randint(0, int(screenDims[1] * .75))
                else:
                    csector = m.teamToSector(self.teamnum)
                    if(csector != False):
                        spawnx = randint(int(csector[0][0]), int(csector[0][1]))
                        spawny = randint(int(csector[1][0]), int(csector[1][1]))

                        self.xPos = spawnx
                        self.yPos = spawny
                    else:
                        print("teamnum spawn failed " + cteamnum)
                        spawnx = 50
                        spawny = 50

                self.isDead = False
                self.hasExploded = False

            else:
                self.hea += 1
                self.timeToRespawn += 1

        else:
            self.timeToRespawn = -1
        #if self.pnum == 1:
            #print(self.timeToRespawn)

        if self.xPos > mapDims[0]:
            if self.gametype == "standard" or self.gametype == "campaign":
                self.xPos = mapDims[0]
                self.vel *= .88
            else:
                self.xPos = 0
        if self.yPos > mapDims[1]:
            if self.gametype == "standard" or self.gametype == "campaign": 
                self.yPos = mapDims[1]
                self.vel *= .88
            else:
                self.yPos = 0
        if self.xPos < 0: 
            if self.gametype == "standard" or self.gametype == "campaign":
                self.xPos = 0
                self.vel *= .88
            else:
                self.xPos = mapDims[0]
        if self.yPos < 0: 
            if self.gametype == "standard" or self.gametype == "campaign":
                self.yPos = 0
                self.vel *= .88
            else:
                self.yPos = mapDims[1]

        #if self.pnum == 1:
            #print(str(self.xPos) + "  " + str(mapDims[0]))

        self.didHaveUBER = self.hasUBER

    def getShiftedPos(self, xadd, yadd):
        tang = 90 * (math.pi / 180)

        shiftedX = xadd * math.cos(tang) - yadd * math.sin(tang)
        shiftedY = xadd * math.sin(tang) + yadd * math.cos(tang)

        return (shiftedX, shiftedY)

    def show(self, screen, cam):

        for dust in self.dust:
            dust.show(screen, cam)
         
        if not self.isDead:

            self.nimg = pygame.transform.scale(self.realImg, (self.width, self.height))
            self.nimg = images.rot_center(self.nimg, self.ang)

            playerImg = (self.nimg, (self.xPos - cam[0] - self.width / 2, self.yPos - cam[1] - self.height / 2))
            screen.blit(playerImg[0], playerImg[1])

            screen.blit(fonts.rend_onlygoodfont(20, str(self.pnum), (180, 180, 180)), (self.xPos - cam[0] + 60, self.yPos - cam[1] + 60))

            ## hp bars ## healthbars ## health bars
            #pygame.draw.rect(screen, (250, 100, 100), pygame.Rect(self.xPos - cam[0] + 20, self.yPos - cam[1] + 60, -100, 15 ))
            thea = self.hea
            index = 0
            while thea > 0:
                bar1width = thea
                if bar1width > 150:
                    bar1width = 150
                thea -= bar1width
                index += 1
                color = [90 + (18 * index), 190 + (12 * index), 90 + (18 * index)]
                for i in range(0, len(color)):
                    if color[i] > 255: color[i] = 255
                pygame.draw.rect(screen, color, pygame.Rect(self.xPos - cam[0] + self.width / 2 - (4 + (4*index)), self.yPos - cam[1] + 50 + (10*index), -bar1width, 7))

            # team lives
            screen.blit(fonts.rend_onlygoodfont(20, str(self.lives), (180, 180, 180)), (self.xPos - cam[0] - 60, self.yPos - cam[1] - 60))
            for bullet in self.bullets:
                bulletImg = bullet.show(screen, cam)
            
            if self.isSacrificingBlood:
                screen.blit(self.bloodAuraImg, (self.xPos - cam[0] - 40, self.yPos - cam[1] - 40))
                if self.UBERtype == "blood4flame":
                    pygame.draw.circle(screen, (250, 160, 160, 80), (int(self.xPos - cam[0]), int(self.yPos - cam[1])), int(self.flameCircleR), 2)

            if self.isInvincible:
                # circle(Surface, color, pos, radius, width=0)
                shieldR = int(self.shieldTimer / 10 + 10)
                pygame.draw.circle(screen, (250, 240, 160), (int(self.xPos - cam[0]), int(self.yPos - cam[1])), shieldR, 2)
            
            if self.hasUBER:
                screen.blit(self.UBERiconimg, (self.xPos - cam[0] - 100, self.yPos - cam[1] - 100))

            if self.dashCooldown > 0:
                screen.blit(self.dashFlashCooldownImg, (self.xPos - cam[0] + 25, self.yPos - cam[1] - 40))

            if self.shouldShowDashFlash:
                self.dashFlashImg = images.get_image("data/img/flash/" + str(self.dashFlashFrame) + ".png")

                screen.blit(self.dashFlashImg, (self.dashFlashPos[0] - cam[0], self.dashFlashPos[1] - cam[1]))

                self.dashFlashFrame += 1
                if self.dashFlashFrame > 5:
                    self.dashFlashFrame = 0
                    self.shouldShowDashFlash = False

        else:

            if not self.hasExploded:
                if self.explosionFrame <= 11:
                    self.explosionFrame += 1
                    if self.explosionFrame == 2:
                        self.deathSound.set_volume(self.volume)
                        self.deathSound.play()
                    explImg = images.get_image("data/img/explosion/" + str(self.explosionFrame) + ".png")
                    explImg = pygame.transform.scale(explImg, (self.width, self.height))
                    screen.blit(explImg, (self.xPos - cam[0] - self.width / 2, self.yPos - cam[1] - self.height / 2))
                else:
                    self.explosionFrame = 0
                    self.hasExploded = True

    def find_nearby_enemy(self, players, radius=800):
        if self.hea < 33:
            radius *= .33
        elif self.hea < 66:
            radius *= .66

        distFromMid = math.hypot(self.xPos - self.mpbnds[0] / 2, self.yPos - self.mpbnds[1] / 2)
        expectedDistFromMid = 400
        if self.gametype == "arena":
            expectedDistFromMid = 150
        if distFromMid < expectedDistFromMid and self.aiType != "dormant" and not self.isCreep:
            self.target = (self.mpbnds[0] / 2, self.mpbnds[1] / 2)
            self.isTargetingPlayer = False
			
        else:
            lowestDist = radius

            for player in players:
                if player.teamnum != self.teamnum and not player.isDead:
                    dist = math.hypot(self.xPos - player.xPos, self.yPos - player.yPos)
                    if self.isCreep and (player.isCreep or player.isAi):
                        dist = 9999999

                    if self.isAi and (player.isCreep):
                        dist = 9999999

                    if dist < lowestDist:
                        self.target = (player.xPos, player.yPos)
                        lowestDist = dist
                        self.isTargetingPlayer = True
            
            # failsafe
            if lowestDist == radius:
                if self.aiType != "dormant":
                    self.target = (self.mpbnds[0] / 2, self.mpbnds[1] / 2)
                    self.isTargetingPlayer = False

            if self.target != (self.mpbnds[0] / 2, self.mpbnds[1] / 2):
                self.isTargetingPlayer = True
    
    def swap_uber(self):
        if self.hasSwappedUberBuffer == 0:
            self.UBERtype = ub.get_random_uber()["type"]
            self.UBERiconimg = images.get_image("data/img/ubers/"+self.UBERtype+".png")
            self.hasSwappedUberBuffer = 4

        if self.isSacrificingBlood:
            self.isSacrificingBlood = False

    def ai_turn_to_target(self):
        
        ang = get_angle_from_points(self.xPos, self.yPos, self.target[0], self.target[1]) - 90
        ang %= 360
        self.ang %= 360

        if abs(ang - self.ang) < 6:
            if randint(0, 2) == 1:
                self.turnRight()
            else:
                self.turnLeft()
        elif self.ang > ang:
            self.turnRight()
        else:
            self.turnLeft()

        #if self.lframe % 100 == 0 and self.pnum == 4:
            #print("target : " + str(self.target))
            #print("nang : " + str(ang))
            #print("cang : " + str(self.ang))

        return ang - self.ang


    def propel(self):
        if not self.isDead:
            if self.isSpeedDemon <= 0:
                self.vel += .625
            else:
                self.vel += .825

            if self.isSpeedDemon <= 0:
                self.vel *= .9875
            else:
                self.vel *= .975

            if self.vel > 8.6 and self.isSpeedDemon <= 0:
                self.vel = 8.6
            elif self.vel > 15 and self.isSpeedDemon > 0:
                self.vel = 15

            self.tryDash("up")

    
    def decelerate(self):
        if not self.isDead:
            self.vel *= .9
            if self.dashBuffer < 6 and self.dashBuffer > 0:
                self.tryDash("down")
            self.dashBuffer = 8
    
    def turn(self, mult):
        if not self.isDead:
            if self.isSpeedDemon <= 0:
                self.turnVel -= ((self.headTurningSharpness - (self.vel * .675)) / 4) * mult
                if self.turnVel > 5.35: self.turnVel = 5.35
            else:
                self.turnVel -= ((self.headTurningSharpness - 1) / 4) * mult
                if self.turnVel > 6: self.turnVel = 6

    def tryDash(self, dir):
        dirToAng = {"up": 90, "left": 180, "right": 0, "down": 270}
        if self.dashCooldown == 0 and self.dashBuffer > 0 and not self.isCreep:
            self.shouldShowDashFlash = True
            self.dashFlashPos = (self.xPos, self.yPos)

            self.dashFlashSound.set_volume(self.volume)
            self.dashFlashSound.play()

            self.xPos += 85 * math.cos((self.ang + dirToAng[dir]) * (math.pi / 180))
            self.yPos += -85 * math.sin((self.ang + dirToAng[dir]) * (math.pi / 180))
            self.dashCooldown = 100
            self.vel *= 1.2
    
    def predictPlacement(self, framesAhead):
        tvel = self.vel * framesAhead
        txvel = tvel * math.cos((self.ang + 90) * (math.pi / 180))
        tyvel = -tvel * math.sin((self.ang + 90) * (math.pi / 180))
        xPos = self.xPos
        yPos = self.yPos
        xPos += txvel
        yPos += tyvel
        return (xPos, yPos)


    def turnRight(self):
        self.turn(1)
        if not self.isDead:
            self.tryDash("right")

    def turnLeft(self):
        self.turn(-1)
        if not self.isDead:
            self.tryDash("left")

    def fire(self):
        if not self.isDead:
            if not self.isCreep:
                if self.timeToFire == 0:
                    barrelPos = self.getShiftedPos(self.width / 5, 0)

                    if not self.hasUBER:

                        self.bullets.append(Bullet((self.xPos + barrelPos[0], self.yPos + barrelPos[1], 12, 48), self.ang, 20, maxLifetime=40))
                        self.timeToFire = 25
                        self.timeToDoubleShot = 7

                        self.fireSound.set_volume(self.volume)
                        self.fireSound.play()
                    
                    else:
                        # ubers

                        if self.UBERtype == "ball":
                            barrelPos = self.getShiftedPos(0, 0)
                            self.bullets.append(Bullet((self.xPos + barrelPos[0], self.yPos + barrelPos[1], int(self.width * 2.2), int(self.height * 2.2)), self.ang, 13, isball=True) )
                            self.vel -= 5
                        
                        elif self.UBERtype == "shield":
                            self.isInvincible = True
                            self.shieldTimer = 300

                        elif self.UBERtype == "scatter":
                            for i in range(-2, 3):
                                sang = self.ang + (i * 5)
                                self.bullets.append(Bullet((self.xPos, self.yPos, 30, 58), sang, 20))
                                
                        elif self.UBERtype == "missile":
                            splitBullet = Bullet((self.xPos + barrelPos[0], self.yPos + barrelPos[1], 52, 78), self.ang, 20, ismissile=True)
                            splitBullet.lifetime = splitBullet.maxLifetime / 4 * 3.4
                            self.bullets.append(splitBullet)

                        elif self.UBERtype == "heal":
                            self.hea = self.maxhea
                            self.hearegen += 0.01

                        elif self.UBERtype == "speed":
                            self.isSpeedDemon = 350

                        elif self.UBERtype == "sniper":
                            barrelPos = self.getShiftedPos(0, 0)
                            sniperBullet = Bullet((self.xPos + barrelPos[0], self.yPos + barrelPos[1], 48, 72), self.ang, 30)
                            sniperBullet.damage = abs(self.maxhea - self.hea) * 3 + 20
                            self.bullets.append(sniperBullet)
                            self.vel -= 1
                            self.hea -= 20

                        elif self.UBERtype[:6] == "blood4":
                            self.isSacrificingBlood = True
                            self.isSacBloodBuffer = 30
                            
                        if self.UBERtype[:6] != "blood4":
                            self.UBERtype = ub.get_random_uber()["type"]
                        self.hasUBER = False

            elif self.isCreep:
                if self.timeToFire == 0:
                    
                    nx = self.xPos + 90 * math.cos((self.ang + 90) * (math.pi / 180))
                    ny = self.yPos - 90 * math.sin((self.ang + 90) * (math.pi / 180))

                    meleeBullet = Bullet((nx, ny, 70, 70), self.ang, 2, isMelee=True, maxLifetime=4)
                    self.bullets.append(meleeBullet)
                    self.timeToFire = 35
                    self.timeToDoubleShot = 14

                    self.fireSound.set_volume(self.volume)
                    self.fireSound.play()

def abs(num):
    if num >= 0: return num
    else: return num * -1

def get_angle_from_points(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    rads = math.atan2(-dy, dx)
    rads %= 2*math.pi
    degs = math.degrees(rads)

    return degs
