import pygame
import json
import io
from random import randint
from functions import images
from classes import player as pl
from classes import background as b
from classes import mines as mn
from classes import spacebase as spb
import math
from functions import mapp as m
from functions import fonts

processingBuffer = [200, 200]

def is_correct_draw_pos(drawpos, wh, processingBuffer):
    shouldDraw = True
    if drawpos[0] > width + processingBuffer[0] + wh[0] / 2 or drawpos[0] < -processingBuffer[0] - wh[0] / 2:
        shouldDraw = False

    if drawpos[1] > height + processingBuffer[1] + wh[1] / 2 or drawpos[1] < -processingBuffer[1] - wh[1] / 2:
        shouldDraw = False

    return shouldDraw

        
screen.convert()
screen.fill((15, 15, 15))
onlygoodfont = pygame.font.Font("data/font/PressStart2P.ttf", 68)
status = -1

gameHasBeenWon = False

try:
    optionsf = open("options.json", "r")
except:
    print("whoa, no options file found.")

try:
    optionsd = json.loads(optionsf.read())
except:
    print("whoa, an empty options file")

if optionsd["gametype"] == "campaign":
    try:
        lvlf = open("data/lvls/lvls.json", "r")
    except:
        print("whoa, no level files found.")

    try:
        savef = open("data/lvls/save.json", "r+")
    except:
        print("whoa, no save file found.")
    
    try:
        lvld = json.loads(lvlf.read())
    except:
        print("whoa, an empty level file")

    try:
        saved = json.loads(savef.read())
    except:
        print("whoa, an empty save file. Like, really empty.")

    clvld = lvld[str(optionsd["level"])]

if randint(0, 2) == 1:
    pygame.mixer.music.load("data\\sound\\venom.mp3")
else:
    pygame.mixer.music.load("data\\sound\\fountain_of_dreams.mp3")
pygame.mixer.music.set_volume(optionsd["mvol"] / 100)
pygame.mixer.music.play(-1)

screen = pygame.display.get_surface()
width = screen.get_width()
height = screen.get_height()


motionBluryness = 145

gdone = False
BackGround = b.Background("data\\img\\background.png", [0, 0, width * 2, height * 2])
nimg = BackGround.image.convert()
nimg.set_alpha((255 - motionBluryness))

clock = pygame.time.Clock()
players = list()
keys = list()
frame = 0
cam = [0, 0, 1]
isplaying = True
cplayernum = 1
startLives = int(optionsd["local_game"]["startlives"]) - 1
if startLives > 10: startLives = 10
if startLives < 1: startLives = 1
teamlives = {"1": startLives, "2": startLives, "3": startLives, "4": startLives}
if optionsd["gametype"] == "campaign":
    teamlives = clvld["lives"]

mines = []
spacebases = []
neutralSectors = m.get_neutral_sectors()
upgrades = []

# SPAWNING
spawnx = 0
spawny = 0
cteamnum = 1

## joysticks
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()

if optionsd["gametype"] == "campaign":
    m.mapBounds = clvld["mapBounds"]
    m.mapSectors = m.refresh_map_sectors()
    optionsd["difficulty"] = clvld["difficulty"]

    for player in clvld["Players"]:
        npl = pl.Player(player[0], player[1], player[2], player[3], player[4], player[5])
        npl.gametype = "campaign"
        npl.mpbnds = m.mapBounds
        players.append(npl)

    for ai in clvld["Ai"]:
        try:
            nai = pl.Player(ai[0], ai[1], ai[2], ai[3], ai[4], ai[5], isAi=True)
            nai.aiType = ai[6]
            nai.gametype = "campaign"
            nai.mpbnds = m.mapBounds
            players.append(nai)
        except:
            pass
            #print("no ai")

    for mine in clvld["Mines"]:
        if mine != []:
            nmine = mn.Mine(mine)
            mines.append(nmine)

    for marker in clvld["Markers"]:
        nmarker = mn.Upgrade(marker[0], isMarker=True, markerText=marker[1], canBePickedUp=marker[2])
        upgrades.append(nmarker)

    for upgrade in clvld["Upgrades"]:
        nupgrade = mn.Upgrade(upgrade)
        upgrades.append(nupgrade)

    for creep in clvld["Creeps"]:
        npl = pl.Player(creep[0], creep[1], creep[2], creep[3], creep[4], creep[5], isCreep=True, isAi=True)
        npl.gametype = "standard"
        npl.mpbnds = m.mapBounds
        players.append(npl)

#print(m.get_map_bounds())

if optionsd["gametype"] == "standard":
    m.mapBounds = [5500, 5500]
    spacebases.append(spb.SpaceBase((m.mapBounds[0] / 2, m.mapBounds[1] / 2, 300, 300)))
elif optionsd["gametype"] == "arena":
    m.mapBounds = [width, height]
    spacebases.append(spb.SpaceBase((width / 2, height / 2, 250, 250)))
elif optionsd["gametype"] == "campaign":
    for spacebase in clvld["spaceBases"]:
        spacebases.append(spb.SpaceBase(spacebase))

if optionsd["gametype"] == "standard":
    for csector in neutralSectors:
        for j in range(0, randint(int(m.mapBounds[0] / 2000), int(m.mapBounds[0] / 600))):
            spawnx = randint(int(csector[0][0]), int(csector[0][1]))
            spawny = randint(int(csector[1][0]), int(csector[1][1]))
            mines.append(mn.Mine([spawnx, spawny, 60, 60]))


if optionsd["gametype"] == "standard":
    for i in range(0, int(optionsd["local_game"]["players"])):
        csector = m.teamToSector(cteamnum)
        spawnx = randint(int(0), int(width))
        spawny = randint(int(0), int(height))

        player = pl.Player([spawnx, spawny, 105, 105], randint(0, 360), 0.2, cteamnum, cplayernum, optionsd["local_game"]["players"] * (20 * (11 - optionsd["local_game"]["difficulty"])), isAi=False)
        player.mpbnds = m.mapBounds
        players.append(player)
        cplayernum += 1
        
    cteamnum += 1
    for i in range(0, int(optionsd["local_game"]["ai"])):

        #if optionsd["gametype"] == "standard":
        csector = m.teamToSector(cteamnum)
        if(csector != False):
            spawnx = randint(int(csector[0][0]), int(csector[0][1]))
            spawny = randint(int(csector[1][0]), int(csector[1][1]))
        else:
            print("teamnum spawn failed " + str(cteamnum))
            spawnx = 50
            spawny = 50

        #else:
            #spawnx = randint(0, width)
            #spawny = randint(0, height)

        teams = optionsd["local_game"]["teams"]
        player = pl.Player([spawnx, spawny, 105, 105], randint(0, 360), 0.2, cteamnum, cplayernum, optionsd["local_game"]["players"] * (100 + optionsd["local_game"]["difficulty"] * 2), isAi=True)
        player.mpbnds = m.mapBounds
        players.append(player)
        
        if(cplayernum % optionsd["local_game"]["players"] == 0):
            cteamnum += 1
        cplayernum += 1

elif optionsd["gametype"] == "arena":

    actors = int(optionsd["local_game"]["ai"] + optionsd["local_game"]["players"])
    if optionsd["local_game"]["teams"] > actors:
        optionsd["local_game"]["teams"] = actors
    teamsize = math.floor(actors / optionsd["local_game"]["teams"] + .98)
    cteamnum = 1
    for i in range(1, actors + 1):
        spawnx = randint(0, width)
        spawny = randint(0, height)
        if i > optionsd["local_game"]["players"]:
            player = pl.Player([spawnx, spawny, 105, 105], randint(0, 360), 0.2, cteamnum, i, optionsd["local_game"]["players"] * (100 + optionsd["local_game"]["difficulty"] * 2), isAi=True)
            print("created AI,  team: " + str(cteamnum) + "   pnum: " + str(i))
        else:
            player = pl.Player([spawnx, spawny, 105, 105], randint(0, 360), 0.2, cteamnum, i, optionsd["local_game"]["players"] * (100), isAi=False)
            print("created player,  team: " + str(cteamnum) + "   pnum: " + str(i))
        player.mpbnds = m.mapBounds
        player.hasStaticVolume = True
        player.gametype = "arena"
        players.append(player)
        if i % teamsize == 0:
            cteamnum += 1

minimwidth = 275
minimheight = 275
minimap = pygame.Surface((minimwidth, minimheight))
minimap = minimap.convert()
minimap.set_alpha(170)

## upgrades
spawnChanceOfUpgrade = 480
upgradesToSpawn = 7
if optionsd["gametype"] == "standard":
    spawnChanceOfUpgrade = 400

sframe = 1
while not gdone:
    frame += 1
    frame %= 10000

    if(sframe >= 0):
        sframe += 1
        if(sframe > 20000):
            sframe = -1

    #print(str(keys))


    # actually get key input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gdone = True
            optionsf.close()

        if event.type == pygame.KEYDOWN:
            keys.append(event.key)
            #print("adding " + str(event.key))
            
        elif event.type == pygame.KEYUP:
            if event.key in keys: 
                keys.remove(event.key)    
                #print("removing " + str(event.key))

        elif event.type == pygame.JOYBUTTONDOWN: ## joysticks
            keys.append("J" + str(event.joy) + str(event.button))
        
        elif event.type == pygame.JOYBUTTONUP:
            keys.remove("J" + str(event.joy) + str(event.button))

        elif event.type == pygame.JOYAXISMOTION:
            #print("value: " + str(event.value) + "  axis: " + str(event.axis) + "  id: " + str(event.joy))
            posOrNeg = "-"
            if event.value > 0:
                posOrNeg = "+"
            if event.value > .2 or event.value < -.2:
                try:
                    keys.remove("JA" + str(event.joy) + str(event.axis) + posOrNeg)
                except:
                    pass
                keys.append("JA" + str(event.joy) + str(event.axis) + posOrNeg)
            
            negOrPos = "+"
            if event.value > 0:
                negOrPos = "-"
            try:
                keys.remove("JA" + str(event.joy) + str(event.axis) + negOrPos)
            except:
                pass

            if event.value < .2 and event.value > -.2:
                try:
                    keys.remove("JA" + str(event.joy) + str(event.axis) + negOrPos)
                except:
                    pass
                try:
                    keys.remove("JA" + str(event.joy) + str(event.axis) + posOrNeg)
                except:
                    pass

    
    if isplaying:

        ## spawn mines and upgrades
        ## mines
        if optionsd["gametype"] == "standard" or (optionsd["gametype"] == "campaign" and clvld["shouldSpawnMines"]):
            if randint(0, 300) == 1:
                for csector in neutralSectors:
                    spawnx = randint(int(csector[0][0]), int(csector[0][1]))
                    spawny = randint(int(csector[1][0]), int(csector[1][1]))
                    tmine = mn.Mine([spawnx, spawny, 60, 60])
                    mines.append(tmine)

        ## upgrades
        if randint(0, spawnChanceOfUpgrade) == 2:
            if optionsd["gametype"] == "standard" or (optionsd["gametype"] == "campaign" and clvld["shouldSpawnUpgrades"]):
                for csector in neutralSectors:
                    if(randint(0, 10 - upgradesToSpawn) == 1):
                        spawnx = randint(int(csector[0][0]), int(csector[0][1]))
                        spawny = randint(int(csector[1][0]), int(csector[1][1]))
                        tupgrade = mn.Upgrade([spawnx, spawny, 80, 80])
                        upgrades.append(tupgrade)
                        #print("spawning upgrade " + str(tupgrade))

            if optionsd["gametype"] == "arena":
                spawnx = randint(0, width)
                spawny = randint(0, height)
                tupgrade = mn.Upgrade([spawnx, spawny, 80, 80])
                tupgrade.hasStaticVolume = True
                upgrades.append(tupgrade)
                    

        
        # minimap
        minimap.fill((160, 160, 160))


        # parse key input
        # keys
        for key in keys:

            if key == pygame.K_ESCAPE:
                gdone = True

            for i in range(0, len(players)):
                if not players[i].isAi:
                    if key == optionsd["player"+str(players[i].pnum)]["up"]:
                        players[i].propel()
                    
                    if key == optionsd["player"+str(players[i].pnum)]["left"]:
                        players[i].turnLeft()

                    if key == optionsd["player"+str(players[i].pnum)]["right"]:
                        players[i].turnRight()

                    if key == optionsd["player"+str(players[i].pnum)]["down"]:
                        players[i].decelerate()

                    if key == optionsd["player"+str(players[i].pnum)]["fire"]:
                        players[i].fire()

                    if key == optionsd["player"+str(players[i].pnum)]["swapuber"]:
                        players[i].swap_uber()

                        #print("FIRE!")

        #print(keys)
        #print(len(players))

        
        cam = [0, 0, 1]
        if optionsd["gametype"] == "standard" or optionsd["gametype"] == "campaign":
            for player in players:
                if player.teamnum == 1:
                    cam[0] += player.xPos
                    cam[1] += player.yPos
            
            if optionsd["gametype"] == "standard":
                cam[0] /= optionsd["local_game"]["players"]
                cam[1] /= optionsd["local_game"]["players"]
            else:
                cam[0] /= len(clvld["Players"])
                cam[1] /= len(clvld["Players"])
            cam[0] -= width / 2
            cam[1] -= height / 2


        #if frame % 500 == 0:
            #print("\n")
            #print(str(width / 2 + players[0].xPos - cam[0]) + " " + str(width / 2 + players[1].xPos - cam[0]))
            #print(str(height / 2 + players[0].yPos - cam[1]) + " " + str(height / 2 + players[1].yPos - cam[1]))
        
        
        ## SPACEBASE PULSE -> MAX HEA OF PLAYER
        for spacebase in spacebases:
            spacebase.tick()
            if spacebase.pulser == 0 and spacebase.pulseteam >= 1 and spacebase.pulseteam <= 4:
                for i in range(0, len(players)):
                    if players[i].teamnum == spacebase.pulseteam:
                        players[i].maxhea += spacebase.maxHeaGiveout
        
        # player interaction
        teamsToBuff = []
        teamsToNerf = []

        for i in range(0, len(players)):

            # brotherly dying 
            if players[i].checkIfDying():
                if optionsd["gametype"] == "standard" or (optionsd["gametype"] == "campaign" and clvld["brotherlyDying"] == True):
                    for j in range(0, len(players)):
                        if players[j].teamnum == players[i].teamnum:
                            players[j].isDead = True
                            players[j].hea = 0
                else:
                    players[i].isDead = True
                    players[i].hea = 0
                try:
                    if not players[i].isCreep:
                        teamlives[str(players[i].teamnum)] -= 1
                except:
                    pass
            
            players[i].tick(m.mapBounds, teamlives, (width, height))
            players[i].volume = players[i].get_volume(optionsd["svol"], cam)

            # minimap
            minix = players[i].xPos / m.mapBounds[0] * minimwidth
            miniy = players[i].yPos / m.mapBounds[1] * minimheight
            if players[i].isAi:
                miniRect = pygame.Rect((minix - 3, miniy - 3), (6, 6))
            else:
                miniRect = pygame.Rect((minix - 5, miniy - 5), (10, 10))
            pygame.draw.rect(minimap, players[i].get_team_color(), miniRect)

            # collision with bullets ( if this player (i) is getting shot by another player (j) )
            for j in range(0, len(players)):
                if players[j].teamnum != players[i].teamnum and not players[j].isDead and not players[i].isDead:
                #if players[i].pnum != players[j].pnum:
                    for bullet in players[j].bullets:
                        if bullet.isTouchingCircle((players[i].xPos, players[i].yPos), players[i].r):
                            if not players[i].isInvincible:
                                players[i].hea -= bullet.damage
                            trueBulletVel = bullet.get_velocity()
                            players[i].xPos += trueBulletVel[0] * (bullet.damage / 100)
                            players[i].yPos += trueBulletVel[1] * (bullet.damage / 100)
                            if not players[i].isInvincible:
                                teamsToBuff.append((players[j].teamnum, players[i].maxhea / optionsd["local_game"]["players"]))
                                teamsToNerf.append(players[i].teamnum)

                            players[i].playhitsound()
                            if not bullet.isPentagram:
                                players[j].bullets.remove(bullet)
            
            # collision with players
            ## flame shield ## flameshield
            for j in range(0, len(players)):
                if players[j].teamnum != players[i].teamnum and not players[j].isDead and not players[i].isDead:
                    if players[i].isTouchingFlame((players[j].xPos, players[j].yPos), players[j].r):
                        players[j].hea -= 2.5

            # shooting up mines
            for bullet in players[i].bullets:
                for mine in mines:
                    if bullet.isTouchingCircle((mine.xPos, mine.yPos), mine.r):
                        mine.isDead = True
                        try:
                            if not bullet.isPentagram:
                                players[i].bullets.remove(bullet)
                        except:
                            pass

            # collision with mines
            for mine in mines:
                mine.volume = mine.get_volume(optionsd["svol"], cam)
                if not mine.isDead and mine.isTouchingCircle((players[i].xPos, players[i].yPos), players[i].r):
                    if not players[i].isInvincible:
                        players[i].hea -= mine.damage
                    mine.isDead = True

                if mine.explosionFrame >= 12:
                    try:
                        mines.remove(mine)
                    except:
                        pass

            # pickup upgrades
            if not players[i].isDead:
                for upgrade in upgrades:
                    upgrade.volume = upgrade.get_volume(optionsd["svol"], cam)
                    if not upgrade.isDead and upgrade.isTouchingCircle((players[i].xPos, players[i].yPos), players[i].r):
                        if not upgrade.isMarker:
                            players[i].hea += 2
                            players[i].hasUBER = True

                        if upgrade.canBePickedUp:
                            upgrade.isDead = True
                            upgrade.frame = 10

                    if upgrade.explosionFrame >= 6:
                        try:
                            upgrades.remove(upgrade)
                        except:
                            pass
                    
                    if upgrade.isDead and upgrade.frame < -1:
                        upgrades.remove(upgrade)

            # spacebase healing
            for spacebase in spacebases:
                if not players[i].isDead:
                    if spacebase.isTouchingCircle((players[i].xPos, players[i].yPos), players[i].r):
                        spacebase.pulsecolor = players[i].get_team_color()
                        players[i].hea += spacebase.healingCapacity
                        spacebase.hasHealed()
                        spacebase.pulseteam = players[i].teamnum
                        #print(str(i) + "    " + str(spacebase.healingCapacity))
                    
            
            # steal max hea

            for team in teamsToBuff:
                for player in players:
                    if player.teamnum == team[0]:
                        player.maxhea += .7 + (team[1] / 3000)

            for team in teamsToNerf:
                for player in players:
                    if player.teamnum == team:
                        player.maxhea -= .3

            ## ai ## artifical intelligence        ~~oooo spooky~~
            # preamble: i want to die. why didn't i go with networking
            if players[i].isAi:
                players[i].find_nearby_enemy(players)

                if optionsd["local_game"]["difficulty"] >= 4:
                    for upgrade in upgrades:
                        dist = math.hypot(players[i].xPos - upgrade.xPos, players[i].yPos - upgrade.yPos)
                        if dist < players[i].vel * 30 and dist > players[i].vel * 7:
                            players[i].target = (upgrade.xPos, upgrade.yPos)

                if players[i].hasUBER:
                    if optionsd["local_game"]["difficulty"] < 6:
                        if not players[i].isSacrificingBlood or optionsd["local_game"]["difficulty"] < 3:
                            if randint(0, 10) == 2:
                                players[i].swap_uber()
                    
                    if players[i].hea < 50 and players[i].UBERtype[:6] == "blood4":
                        players[i].swap_uber()
                    
                if optionsd["local_game"]["difficulty"] > 4:
                    if players[i].isSacrificingBlood and players[i].hea < 40:
                        players[i].swap_uber()

                angleToGo = players[i].ai_turn_to_target()
                if angleToGo < 60 or angleToGo > 300:
                    if players[i].aiType != "dormant" and not players[i].isCreep:
                        players[i].propel()
                    elif math.hypot(players[i].xPos - players[i].target[0], players[i].yPos - players[i].target[1]) < 900:
                        if not (players[i].aiType == "dormant" and not players[i].isTargetingPlayer):
                            players[i].propel()

                if angleToGo > 150 and angleToGo < 210 and players[i].lframe % 2 == 0:
                    players[i].decelerate()
                    if optionsd["local_game"]["difficulty"] > 5:
                        players[i].tryDash("down")

                if players[i].isTargetingPlayer:
                    if not players[i].isCreep and players[i].aiType != "dormant":
                        players[i].fire()
                    elif math.hypot(players[i].xPos - players[i].target[0], players[i].yPos - players[i].target[1]) < 1200:
                        players[i].fire()

                if optionsd["local_game"]["difficulty"] >= 2:
                    for mine in mines:
                        pPos = players[i].predictPlacement(10)
                        dist = math.hypot(mine.xPos - pPos[0], mine.yPos - pPos[1])
                        if dist < players[i].vel * 5:
                            players[i].decelerate()
                            if randint(0, 2) == 1:
                                players[i].tryDash("right")
                            else:
                                players[i].tryDash("left")
                            
                if optionsd["local_game"]["difficulty"] > 6:
                    for enemy in players:
                        if enemy.teamnum != players[i].teamnum:
                            for bullet in enemy.bullets:
                                dist = math.hypot(bullet.xPos - players[i].xPos, bullet.yPos - players[i].yPos)

                                if dist < int(players[i].r * 2.5):
                                    bullet.ang %= 360
                                    bang = abs(bullet.ang - players[i].ang)
                                    
                                    toExclude = ""
                                    if optionsd["local_game"]["difficulty"] >= 7.75:
                                        if bang > 30 and bang < -30:
                                            toExclude = "up"
                                        if bang > 150 and bang < 210:
                                            toExclude = "down"
                                        if bang > 60 and bang < 120:
                                            toExclude = "right"
                                        if bang > 240 and bang < 300:
                                            toExclude = "left"
                                    
                                    relationDict = {0: "up", 1: "right", 2: "down", 3: "left"}
                                    trand = randint(0, 3)
                                    while relationDict[trand] == toExclude:
                                        trand = randint(0, 3)

                                    players[i].decelerate()
                                    players[i].tryDash(relationDict[trand])

            # nevermind was pretty easy
                

        for mine in mines:
            if mine.explosionFrame >= 12:
                mines.remove(mine)

        # backgrounds
        #Backrect = pygame.Rect(BackGround.rect.left - (cam[0] / width * 20), BackGround.rect.top - (cam[1] / height * 20), BackGround.rect.width, BackGround.rect.height)
        #screen.blit(nimg, Backrect)

        # border
        if optionsd["gametype"] != "arena":
            pygame.draw.rect(screen, (200, 100, 100), pygame.Rect(-cam[0], -cam[1], m.mapBounds[0], m.mapBounds[1]), 10)


        # show actors in order of overlay (lowest -> highest)
        for spacebase in spacebases:
            drawpos = spacebase.get_draw_pos(cam)
            wh = spacebase.get_wh()
            shouldDraw = is_correct_draw_pos(drawpos, wh, processingBuffer)
            if shouldDraw:
                spacebase.show(screen, cam)

        for player in players:
            player.show(screen, cam)

        for mine in mines:
            mine.show(screen, cam)

        for upgrade in upgrades:
            upgrade.show(screen, cam)

            if not upgrade.isMarker:
                upgrdRect = pygame.Rect((upgrade.xPos / m.mapBounds[0] * minimwidth - 1, upgrade.yPos / m.mapBounds[1] * minimheight - 1), (3, 3))
                pygame.draw.rect(minimap, (200, 180, 50), upgrdRect)
            else:
                upgrdRect = pygame.Rect((upgrade.xPos / m.mapBounds[0] * minimwidth - 3, upgrade.yPos / m.mapBounds[1] * minimheight - 3), (6, 6))
                pygame.draw.rect(minimap, (150, 150, 250), upgrdRect)
        
        # scoreboard overlay beep boop im a robot ## leaderboard
        teammHeas = {}
        teamLives = {}
        teamColors = {}

        for player in players:
            teammHeas[player.teamnum] = int(player.maxhea - (optionsd["local_game"]["players"] * 100))
            teamColors[player.teamnum] = player.get_team_color()
            teamLives[str(player.teamnum)] = player.lives

        tteams = int(optionsd["local_game"]["teams"] + 1)
        if optionsd["gametype"] == "campaign":
            tteams = int(clvld["teams"])
        
        for i in range(1, tteams):
            winAmt = 300
            if optionsd["gametype"] == "arena":
                winAmt = 500
            try:
                if teammHeas[i] >= winAmt and not gameHasBeenWon:
                    print(str(i) + " has won")
                    screen.blit(fonts.rend_onlygoodfont(80, "TEAM "+str(i)+" WINS", teamColors[i]), (300, 300))
                    isplaying = False
                    gameHasBeenWon = True

                if teamLives[str(i)] > 0 and not gameHasBeenWon:
                    losers = 0
                    for j in range(1, int(optionsd["local_game"]["teams"] + 1)):
                        if j != i:
                            if teamLives[str(j)] < 0:
                                losers += 1

                    if losers == int(optionsd["local_game"]["teams"]) - 1:
                        print(str(i) + " has won")
                        screen.blit(fonts.rend_onlygoodfont(80, "TEAM "+str(i)+" WINS", teamColors[i]), (300, 300))
                        isplaying = False
                        gameHasBeenWon = True
            except:
                pass
        if optionsd["gametype"] == "campaign" and clvld["winOnNoMarkers"]:
            noMarkersLeft = True
            for upgrade in upgrades:
                if upgrade.isMarker and not upgrade.isDead and upgrade.canBePickedUp:
                    noMarkersLeft = False

            if noMarkersLeft and not gameHasBeenWon:
                screen.blit(fonts.rend_onlygoodfont(70, "All markers collected!", (100, 200, 100) ), (100, 300) )
                screen.blit(fonts.rend_onlygoodfont(70, "Press Esc to quit.", (100, 200, 100) ), (100, 400) )
                ## game won by markers
                isplaying = False
                gameHasBeenWon = True

        
        if optionsd["gametype"] != "campaign":
            tteams -= 1
        screen.blit(fonts.rend_onlygoodfont(28, "SCORES: ", (180, 180, 180)), (100, 80))

        try:
            if tteams >= 1:
                screen.blit(fonts.rend_onlygoodfont(32, str(teammHeas[1]), teamColors[1]), (200, 125))
                screen.blit(fonts.rend_onlygoodfont(32, str(teamLives["1"]), teamColors[1]), (230, 160))
            if tteams >= 2:
                screen.blit(fonts.rend_onlygoodfont(32, str(teammHeas[2]), teamColors[2]), (300, 90))
                screen.blit(fonts.rend_onlygoodfont(32, str(teamLives["2"]), teamColors[2]), (330, 55))
            if tteams >= 3:
                screen.blit(fonts.rend_onlygoodfont(32, str(teammHeas[3]), teamColors[3]), (400, 125))
                screen.blit(fonts.rend_onlygoodfont(32, str(teamLives["3"]), teamColors[3]), (430, 160))
            if tteams >= 4:
                screen.blit(fonts.rend_onlygoodfont(32, str(teammHeas[4]), teamColors[4]), (500, 90))
                screen.blit(fonts.rend_onlygoodfont(32, str(teamLives["4"]), teamColors[4]), (530, 55))
        except:
            pass


        # minimap  
        pygame.draw.line(minimap, (125, 250, 225), (minimwidth / 3, 0), (minimwidth / 3, minimheight))
        pygame.draw.line(minimap, (125, 250, 225), (minimwidth / 3 * 2, 0), (minimwidth / 3 * 2, minimheight))
        pygame.draw.line(minimap, (125, 250, 225), (0, minimheight / 3), (minimwidth, minimheight / 3))
        pygame.draw.line(minimap, (125, 250, 225), (0, minimheight / 3 * 2), (minimwidth, minimheight / 3 * 2))

        if optionsd["gametype"] == "standard" or optionsd["gametype"] == "arena":
            spbase = pygame.Rect((minimwidth / 2 - 6, minimheight / 2 - 6), (12, 12))
            pygame.draw.rect(minimap, (spacebases[0].pulsecolor), spbase)

        elif optionsd["gametype"] == "campaign":
            for spbase in spacebases:
                spbaser = pygame.Rect((spbase.xPos / m.mapBounds[0] * minimwidth - 6, spbase.yPos / m.mapBounds[1] * minimheight - 6), (12, 12))
                pygame.draw.rect(minimap, (spbase.pulsecolor), spbaser)

        outline = pygame.Rect((0, 0), (minimwidth - 1, minimheight - 1))
        pygame.draw.rect(minimap, (250, 160, 160), outline, 2)
        screen.blit(minimap, (width - minimwidth, height - minimheight))

        if sframe == 2:
            isplaying = False
            screen.fill((0, 0, 0, 0))
            text = onlygoodfont.render("Ready?", True, (200, 255, 200))
            screen.blit(text, (width / 2 - text.get_width() / 2, (height / 2) - text.get_height() / 2))            
        

        
    else:
        if optionsd["gametype"] == "campaign":
            savef.seek(0)
            savef.truncate()
            if gameHasBeenWon:
                saved["levelsCompleted"][str(optionsd["level"])] = True
            json.dump(saved, savef, indent=3, sort_keys=True)

        if gameHasBeenWon:
            #screen.blit(fonts.rend_onlygoodfont(80, "TEAM "+str(i)+" WINS", teamColors[i]), (300, 300))
            for key in keys:
                if key == pygame.K_ESCAPE:
                    gdone = True

        elif sframe % 60 == 0:
            screen.blit(minimap, (width - minimwidth, height - minimheight))
            screen.fill((0, 0, 0, 200))
            if status <= 0:
                text = onlygoodfont.render("Set", True, (200, 255, 200))

            elif status <= 1:
                text = onlygoodfont.render("GO!", True, (200, 255, 200))

            elif status == 2:
                isplaying = True
                status = 0
                

            status += 1

            screen.blit(text, (width / 2 - text.get_width() / 2, (height / 2) - text.get_height() / 2))
            #print(str(status))

    # double buffering ftw
    if not done:
        pygame.display.flip()
        clock.tick(44) ## 44



def abs(num):
    if num >= 0: return num
    else: return num * -1
