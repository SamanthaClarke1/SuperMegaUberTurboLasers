import pygame
import io
from random import randint
from functions import images
from classes import background as b
import json
import os


# load the options if they're set. If they're not then set the data to the defaults.
optionsf = open('options.json', 'r+')
lvldescsf = open('data/lvls/desc.json', 'r')
savef = open("data/lvls/save.json", "r")
try:
    optionsd = json.loads(optionsf.read())
except:
    print("Options file is empty or broken. Propogating with defaults.")
    optionsd = {
   "gametype": "arena",
   "local_game": {
      "ai": 1,
      "difficulty": 6.0,
      "players": 1,
      "teams": 2,
      "startlives": 5
   },
   "mvol": 8,
   "player1": {
      "down": 115,
      "fire": 32,
      "left": 97,
      "right": 100,
      "swapuber": 304,
      "up": 119
   },
   "player2": {
      "down": "JA0+",
      "fire": "J00",
      "left": "JA0-",
      "right": "JA0+",
      "swapuber": "J01",
      "up": "JA0-"
   },
   "player3": {
      "down": 274,
      "fire": 271,
      "left": 276,
      "right": 275,
      "swapuber": 266,
      "up": 273
   },
   "player4": {
      "down": 104,
      "fire": 47,
      "left": 103,
      "right": 106,
      "swapuber": 39,
      "up": 117
   },
   "sheight": 980,
   "svol": 3,
   "swidth": 1600
}
try:
    lvldescs = json.loads(lvldescsf.read())
except:
    print("broken lvl descriptions file")
try:
    save = json.loads(savef.read())
    lvlsaves = save["levelsCompleted"]
except:
    print("broken save file")

oHandPos = 0
oState = ""
pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.init()
if optionsd["fullscreen"]:
    screen = pygame.display.set_mode((optionsd["swidth"], optionsd["sheight"]), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
else:
    screen = pygame.display.set_mode((optionsd["swidth"], optionsd["sheight"]), pygame.RESIZABLE)

pygame.display.set_caption("S.M.U.T. LASERS", "S.M.U.T.L.")

width = screen.get_width()
height = screen.get_height()

moveSound = pygame.mixer.Sound(os.path.join('data','sound','sfx','menumove.wav'))  #load sound
selectSound = pygame.mixer.Sound(os.path.join('data','sound','sfx','menuselect.wav'))

moveSound.set_volume(optionsd["svol"] / 100)
selectSound.set_volume(optionsd["svol"] / 100)

## joysticks
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()

done = False
clock = pygame.time.Clock()


onlygoodfont = pygame.font.Font("data/font/PressStart2P.ttf", 68)
smallerfont = pygame.font.Font("data/font/PressStart2P.ttf", 38)
fontColor = (200, 200, 200)
greyFontColor = (100, 100, 100)
state = "MENU"
handPos = 0

plimage = pygame.transform.rotate(images.get_image("data/img/player.png"), 270)
plimage = pygame.transform.scale(plimage, (180, 180))


pygame.mixer.music.load("data\\sound\\allstarheal.mp3")

pygame.mixer.music.set_volume(optionsd["mvol"] / 100)
pygame.mixer.music.play(-1)

handX = 60
frame = 0
optionsOnThisPage = 3
cPlayerControls = 1
isInputtingInto = ""
isInputtingTimer = 0
isGreen = True

BackGround = b.Background('data\\img\\background.png', [0,0,width,height])

def getrkey(cPlayerControls, key):
    try:
        if isinstance(optionsd["player" + str(cPlayerControls)][key], int):
            Display = str( pygame.key.name(optionsd["player" + str(cPlayerControls)][key]))
        else:
            Display = optionsd["player" + str(cPlayerControls)][key]
        Display.replace("unknown key", "empty")
    except:
        Display = "empty"

    return Display

## main game loop
while not done:
    frame += 1
    if(isInputtingInto != ""):
        isInputtingTimer += 1
        if(isInputtingTimer % 11 == 0):
            isGreen = not isGreen

        if(isInputtingTimer > 120):
            isInputtingTimer = 0
            isInputtingInto = ""
            isGreen = True

    if(frame % 20 == 0):
        frame = 0
        if(handX == 60): handX = 80
        else: handX = 60


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            optionsf.close()

        ## joysticks
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        #if event.type == pygame.JOYBUTTONDOWN:
            #print("joybutton pressed " + str(event.button))

        #if event.type == pygame.JOYBUTTONUP:
            #print("joybutton released " + str(event.button))

        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            handPos -= 1
            handPos %= optionsOnThisPage

        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            handPos += 1
            handPos %= optionsOnThisPage

        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:

            if state == "CAMPAIGN_PG1":
                if handPos == 0:
                    optionsd["level"] += 1
                    try:
                        optionsd["leveldesc"] = lvldescs[str(optionsd["level"])]
                    except:
                        optionsd["level"] -= 1

            if state == "OPTIONS":
                if handPos == 0:
                    optionsd["mvol"] += 1

                if handPos == 1:
                    optionsd["svol"] += 1
                
                pygame.mixer.music.set_volume(optionsd["mvol"] / 100)

            if state == "CREATING_SINGLE_GAME":
                if optionsd["local_game"]["players"] + optionsd["local_game"]["ai"] < 16:
                    if handPos == 0:
                        if optionsd["local_game"]["players"] < 4:
                            optionsd["local_game"]["players"] += 1
                    
                    if handPos == 1:
                        optionsd["local_game"]["ai"] += 1

                    if handPos == 3:
                        if optionsd["local_game"]["difficulty"] < 10:
                            optionsd["local_game"]["difficulty"] += .25

                    if optionsd["gametype"] == "arena":
                        if handPos == 2:
                            if optionsd["local_game"]["teams"] < 4:
                                optionsd["local_game"]["teams"] += 1

                amtOfActors = optionsd["local_game"]["players"] + optionsd["local_game"]["ai"]
                if optionsd["gametype"] == "standard":
                    optionsd["local_game"]["teams"] = (amtOfActors / optionsd["local_game"]["players"])



            if state == "SCREEN_OPTIONS":
                if handPos == 0:
                    if optionsd["swidth"] < 2280:
                        optionsd["swidth"] += 5
                
                if handPos == 1:
                    if optionsd["sheight"] < 1640:
                        optionsd["sheight"] += 5
                
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:

            if state == "CAMPAIGN_PG1":
                if handPos == 0:
                    optionsd["level"] -= 1
                    try:
                        optionsd["leveldesc"] = lvldescs[str(optionsd["level"])]
                    except:
                        optionsd["level"] += 1

            if state == "OPTIONS":
                if handPos == 0:
                    optionsd["mvol"] -= 1

                if handPos == 1:
                    optionsd["svol"] -= 1

                pygame.mixer.music.set_volume(optionsd["mvol"] / 100)

            if state == "CREATING_SINGLE_GAME":
                if handPos == 0:
                    if optionsd["local_game"]["players"] > 1:
                        optionsd["local_game"]["players"] -= 1
                
                if handPos == 1:
                    if optionsd["local_game"]["ai"] > 0:
                        optionsd["local_game"]["ai"] -= 1

                if handPos == 3:
                    if optionsd["local_game"]["difficulty"] > 1:
                        optionsd["local_game"]["difficulty"] -= .25

                if optionsd["gametype"] == "arena":
                    if handPos == 2:
                        if optionsd["local_game"]["teams"] > 2:
                            optionsd["local_game"]["teams"] -= 1
                
                amtOfActors = optionsd["local_game"]["players"] + optionsd["local_game"]["ai"]
                if optionsd["gametype"] != "arena":
                    optionsd["local_game"]["teams"] = (amtOfActors / optionsd["local_game"]["players"])

            if state == "SCREEN_OPTIONS":
                if handPos == 0:
                    if optionsd["swidth"] > 600:
                        optionsd["swidth"] -= 5
                
                if handPos == 1:
                    if optionsd["sheight"] > 800:
                        optionsd["sheight"] -= 5

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:

            if state == "MENU":
                if handPos == 0:
                    state = "SINGLE_VS_MULTI"
                    optionsOnThisPage = 4
                    handPos = 0
                    
                if handPos == 2:
                    done = True
                    optionsf.close()
                    
                if handPos == 1:
                    state = "OPTIONS"
                    optionsOnThisPage = 5
                    handPos = 0
            
            elif state == "OPTIONS":
                
                if handPos == 2:
                    state = "SETTING_CONTROLS"
                    optionsOnThisPage = 5
                    handPos = 0

                if handPos == 3:
                    state = "SCREEN_OPTIONS"
                    optionsOnThisPage = 3
                    handPos = 0

                if handPos == 4:
                    state = "MENU"
                    optionsf.seek(0)
                    optionsf.truncate()
                    json.dump(optionsd, optionsf, indent=3, sort_keys=True)
                    optionsOnThisPage = 3
                    handPos = 0
            
            elif state == "SINGLE_VS_MULTI":

                if handPos == 0:
                    state = "CREATING_SINGLE_GAME"
                    optionsOnThisPage = 6
                    optionsd["gametype"] = "standard"
                    amtOfActors = optionsd["local_game"]["players"] + optionsd["local_game"]["ai"]
                    optionsd["local_game"]["teams"] = (amtOfActors / optionsd["local_game"]["players"])
                    handPos = 0

                if handPos == 1:
                    #print("arena is not defo in devo. clap clap for your favourite handicap, the dev")
                    # arena
                    optionsd["gametype"] = "arena"
                    state = "CREATING_SINGLE_GAME"
                    optionsd["local_game"]["teams"] = 2
                    optionsOnThisPage = 6
                    handPos = 0
                
                if handPos == 2:
                    state = "CAMPAIGN_PG1"
                    optionsOnThisPage = 4
                    handPos = 0
                    try:
                        optionsd["leveldesc"] = lvldescs[str(optionsd["level"])]
                    except:
                        optionsd["level"] += 1
                    # i wish i did this all better lol

                if handPos == 3:
                    state = "MENU"
                    optionsOnThisPage = 3
                    handPos = 0

            elif state == "CAMPAIGN_PG1":
                
                if handPos == 2 and lvlsaves[str(optionsd["level"] - 1)]:
                    optionsd["gametype"] = "campaign"
                    optionsf.seek(0)
                    optionsf.truncate()
                    json.dump(optionsd, optionsf, indent=3, sort_keys=True)
                    exec(open("game.py").read())
                    optionsf = open('options.json', 'r+')
                    savef.close()
                    savef = open("data/lvls/save.json", "r+")
                    save = json.loads(savef.read())
                    lvlsaves = save["levelsCompleted"]
                    
                if handPos == 3:
                    state = "SINGLE_VS_MULTI"
                    optionsOnThisPage = 4
                    handPos = 0

            elif state == "CREATING_SINGLE_GAME":
                teamsAreCorrect = (optionsd["local_game"]["teams"] == 2 or optionsd["local_game"]["teams"] == 4)
                if optionsd["gametype"] == "arena":
                    teamsAreCorrect = True

                if handPos == 4 and teamsAreCorrect:
                    # open the game ## save the game/options file
                    optionsf.seek(0)
                    optionsf.truncate()
                    json.dump(optionsd, optionsf, indent=3, sort_keys=True)
                    exec(open("game.py").read())
                    optionsf = open('options.json', 'r+')
                    #print("working on this")
                
                if handPos == 5:
                    state = "SINGLE_VS_MULTI"
                    optionsOnThisPage = 4
                    handPos = 0
                    optionsf.seek(0)
                    optionsf.truncate()
                    json.dump(optionsd, optionsf, indent=3, sort_keys=True)

            elif state == "SETTING_CONTROLS":
                
                if handPos < 4:
                    cPlayerControls = handPos + 1
                    state = "SETTING_PLAYER_CONTROLS"
                    optionsOnThisPage = 7
                    handPos = 0

                if handPos == 4:
                    state = "OPTIONS"
                    optionsOnThisPage = 5
                    handPos = 0
            
            elif state == "SETTING_PLAYER_CONTROLS":
                
                if handPos == 0:
                    isInputtingInto = "up"

                if handPos == 1:
                    isInputtingInto = "left"

                if handPos == 2:
                    isInputtingInto = "down"

                if handPos == 3:
                    isInputtingInto = "right"

                if handPos == 4:
                    isInputtingInto = "fire"

                if handPos == 5:
                    isInputtingInto = "swapuber"

                if handPos == 6:
                    state = "SETTING_CONTROLS"
                    optionsOnThisPage = 5
                    handPos = 0
            
            elif state == "SCREEN_OPTIONS":
                if handPos == 2:
                    state = "OPTIONS"
                    optionsOnThisPage = 5
                    handPos = 0
        
        isProperEvent = (event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYAXISMOTION)
        if isInputtingTimer > 0 and isInputtingInto != "" and state == "SETTING_PLAYER_CONTROLS" and isProperEvent:
            if event.type == pygame.KEYDOWN:
                optionsd["player" + str(cPlayerControls)][isInputtingInto] = event.key

            elif event.type == pygame.JOYBUTTONDOWN: ## joysticks
                optionsd["player" + str(cPlayerControls)][isInputtingInto] = "J" + str(event.joy) + str(event.button)

            elif event.type == pygame.JOYAXISMOTION:
                #print("value: " + str(event.value) + "  axis: " + str(event.axis) + "  id: " + str(event.joy))
                posOrNeg = "-"
                if event.value > 0:
                    posOrNeg = "+"
                optionsd["player" + str(cPlayerControls)][isInputtingInto] = "JA" + str(event.joy) + str(event.axis) + posOrNeg

            isInputtingInto = ""
            isInputtingTimer = 0

    screen.fill((15, 15, 15))
    screen.blit(BackGround.image, BackGround.rect)


    ################ DISPLAY ################

    if state == "CAMPAIGN_PG1":

        lvFontCol = (fontColor)
        if not lvlsaves[str(optionsd["level"])]:
            lvFontCol = (greyFontColor)
        text = onlygoodfont.render("Level: " + str(optionsd["level"]), True, (lvFontCol))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 5) - text.get_height() / 2))
        if handPos == 0:
            screen.blit(plimage, (handX, (height / 5) - 90))
        
        descs = str(optionsd["leveldesc"]).split("\n")
        for i in range(0, len(descs)):
            text = smallerfont.render(descs[i], True, (greyFontColor))
            screen.blit(text, (width / 2 - text.get_width() / 2, (height / 5) * 2 + (smallerfont.get_height() * i)))

        if handPos == 1:
            screen.blit(plimage, (handX, (height / 5) * 2 - 90))
        
        playFontCol = (fontColor)
        if not lvlsaves[str(optionsd["level"] - 1)]:
            playFontCol = (greyFontColor)
        text = onlygoodfont.render("Play", True, (playFontCol))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 5) * 3 - text.get_height() / 2))
        if handPos == 2:
            screen.blit(plimage, (handX, (height / 5) * 3 - 90))

        text = onlygoodfont.render("Back", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 5) * 4 - text.get_height() / 2))
        if handPos == 3:
            screen.blit(plimage, (handX, (height / 5) * 4 - 90))

    if state == "SCREEN_OPTIONS":

        text = onlygoodfont.render("Width: " + str(optionsd["swidth"]), True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 4) - text.get_height() / 2))
        if handPos == 0:
            screen.blit(plimage, (handX, (height / 4) - 90))

        text = onlygoodfont.render("Height: " + str(optionsd["sheight"]), True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 4) * 2 - text.get_height() / 2))
        if handPos == 1:
            screen.blit(plimage, (handX, (height / 4) * 2 - 90))

        text = onlygoodfont.render("Back", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 4) * 3 - text.get_height() / 2))
        if handPos == 2:
            screen.blit(plimage, (handX, (height / 4) * 3 - 90))

    if state == "SETTING_PLAYER_CONTROLS":

        Display = getrkey(cPlayerControls, "up")
        if isInputtingInto == "up" and isGreen:
            text = onlygoodfont.render("Up: " + Display, True, (200, 255, 200))
        else:
            text = onlygoodfont.render("Up: " + Display, True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 8) - text.get_height() / 2))
        if handPos == 0:
            screen.blit(plimage, (handX, (height / 8) - 90))

        Display = getrkey(cPlayerControls, "left")
        if isInputtingInto == "left" and isGreen:
            text = onlygoodfont.render("Left: " + Display, True, (200, 255, 200))
        else:
            text = onlygoodfont.render("Left: " + Display, True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 8) * 2 - text.get_height() / 2))
        if handPos == 1:
            screen.blit(plimage, (handX, (height / 8) * 2 - 90))

        Display = getrkey(cPlayerControls, "down")
        if isInputtingInto == "down" and isGreen:
            text = onlygoodfont.render("Down: " + Display, True, (200, 255, 200))
        else:
            text = onlygoodfont.render("Down: " + Display, True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 8) * 3 - text.get_height() / 2))
        if handPos == 2:
            screen.blit(plimage, (handX, (height / 8) * 3 - 90))

        Display = getrkey(cPlayerControls, "right")
        if isInputtingInto == "right" and isGreen:
            text = onlygoodfont.render("Right: " + Display, True, (200, 255, 200))
        else:
            text = onlygoodfont.render("Right: " + Display, True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 8) * 4 - text.get_height() / 2))
        if handPos == 3:
            screen.blit(plimage, (handX, (height / 8) * 4 - 90))

        Display = getrkey(cPlayerControls, "fire")
        if isInputtingInto == "fire":
            text = onlygoodfont.render("Fire: " + Display, True, (200, 255, 200))
        else:
            text = onlygoodfont.render("Fire: " + Display, True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 8) * 5 - text.get_height() / 2))
        if handPos == 4:
            screen.blit(plimage, (handX, (height / 8) * 5 - 90))

        try:
            if isinstance(optionsd["player" + str(cPlayerControls)]["swapuber"], int):
                Display = str( pygame.key.name(optionsd["player" + str(cPlayerControls)]["swapuber"]))
            else:
                Display = optionsd["player" + str(cPlayerControls)]["swapuber"]
            Display.replace("unknown key", "empty")
        except:
            Display = "empty"
        if isInputtingInto == "swapuber":
            text = onlygoodfont.render("Swap Uber: " + Display, True, (200, 255, 200))
        else:
            text = onlygoodfont.render("Swap Uber: " + Display, True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 8) * 6 - text.get_height() / 2))
        if handPos == 5:
            screen.blit(plimage, (handX, (height / 8) * 6 - 90))
                    
        text = onlygoodfont.render("Back", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 8) * 7 - text.get_height() / 2))
        if handPos == 6:
            screen.blit(plimage, (handX, (height / 8) * 7 - 90))

    if state == "SETTING_CONTROLS":

        text = onlygoodfont.render("Player1", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) - text.get_height() / 2))
        if handPos == 0:
            screen.blit(plimage, (handX, (height / 6) - 90))

        text = onlygoodfont.render("Player2", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) * 2 - text.get_height() / 2))
        if handPos == 1:
            screen.blit(plimage, (handX, (height / 6) * 2 - 90))

        text = onlygoodfont.render("Player3", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) * 3 - text.get_height() / 2))
        if handPos == 2:
            screen.blit(plimage, (handX, (height / 6) * 3 - 90))

        text = onlygoodfont.render("Player4", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) * 4 - text.get_height() / 2))
        if handPos == 3:
            screen.blit(plimage, (handX, (height / 6) * 4 - 90))

        text = onlygoodfont.render("Back", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) * 5 - text.get_height() / 2))
        if handPos == 4:
            screen.blit(plimage, (handX, (height / 6) * 5 - 90))

    if state == "CREATING_SINGLE_GAME":
        
        text = onlygoodfont.render("Players: " + str(optionsd["local_game"]["players"]), True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 7) - text.get_height() / 2))
        if handPos == 0:
            screen.blit(plimage, (handX, (height / 7) - 90))

        text = onlygoodfont.render("Bots: " + str(optionsd["local_game"]["ai"]), True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 7) * 2 - text.get_height() / 2))
        if handPos == 1:
            screen.blit(plimage, (handX, (height / 7) * 2 - 90))
        
        teamsFontCol = fontColor
        if optionsd["gametype"] == "standard":
            teamsFontCol = greyFontColor
        text = onlygoodfont.render("Teams: " + str(optionsd["local_game"]["teams"]), True, (teamsFontCol))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 7) * 3 - text.get_height() / 2))
        if handPos == 2:
            screen.blit(plimage, (handX, (height / 7) * 3 - 90))

        text = onlygoodfont.render("Difficulty: " + str(optionsd["local_game"]["difficulty"]), True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 7) * 4 - text.get_height() / 2))
        if handPos == 3:
            screen.blit(plimage, (handX, (height / 7) * 4 - 90))

        playFontColor = greyFontColor
        teamsAreCorrect = (optionsd["local_game"]["teams"] == 2 or optionsd["local_game"]["teams"] == 4)
        if optionsd["gametype"] == "arena":
            teamsAreCorrect = True
        if teamsAreCorrect: playFontColor = fontColor

        text = onlygoodfont.render("Play!", True, (playFontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 7) * 5 - text.get_height() / 2))
        if handPos == 4:
            screen.blit(plimage, (handX, (height / 7) * 5 - 90))

        text = onlygoodfont.render("Back", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 7) * 6 - text.get_height() / 2))
        if handPos == 5:
            screen.blit(plimage, (handX, (height / 7) * 6 - 90))
        

    if state == "SINGLE_VS_MULTI":

        text = onlygoodfont.render("Original Game", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 5) - text.get_height() / 2))
        if handPos == 0:
            screen.blit(plimage, (handX, (height / 5) - 90))

        text = onlygoodfont.render("Arena Game", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 5) * 2 - text.get_height() / 2))
        if handPos == 1:
            screen.blit(plimage, (handX, (height / 5) * 2 - 90))

        text = onlygoodfont.render("Campaign", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 5) * 3 - text.get_height() / 2))
        if handPos == 2:
            screen.blit(plimage, (handX, (height / 5) * 3 - 90))

        text = onlygoodfont.render("Back", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 5) * 4 - text.get_height() / 2))
        if handPos == 3:
            screen.blit(plimage, (handX, (height / 5) * 4 - 90))


    if state == "OPTIONS":

        text = onlygoodfont.render("Music Vol: " + str(optionsd["mvol"]), True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) - text.get_height() / 2))
        if handPos == 0:
            screen.blit(plimage, (handX, (height / 6) - 90))

        text = onlygoodfont.render("SFX Vol: " + str(optionsd["svol"]), True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) * 2 - text.get_height() / 2))
        if handPos == 1:
            screen.blit(plimage, (handX, (height / 6) * 2 - 90))

        text = onlygoodfont.render("Controls", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) * 3 - text.get_height() / 2))
        if handPos == 2:
            screen.blit(plimage, (handX, (height / 6) * 3 - 90))

        text = onlygoodfont.render("Screen", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) * 4 - text.get_height() / 2))
        if handPos == 3:
            screen.blit(plimage, (handX, (height / 6) * 4 - 90))

        text = onlygoodfont.render("Save & Back", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 6) * 5 - text.get_height() / 2))
        if handPos == 4:
            screen.blit(plimage, (handX, (height / 6) * 5 - 90))


    if state == "MENU":

        text = onlygoodfont.render("Play", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, height / 4 - text.get_height() / 2))
        if handPos == 0:
            screen.blit(plimage, (handX, height / 4 - 90))

        text = onlygoodfont.render("Options", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 4) * 2 - text.get_height() / 2))
        if handPos == 1:
            screen.blit(plimage, (handX, (height / 4) * 2 - 90))

        text = onlygoodfont.render("Exit", True, (fontColor))
        screen.blit(text, (width / 2 - text.get_width() / 2, (height / 4) * 3 - text.get_height() / 2))
        if handPos == 2:
            screen.blit(plimage, (handX, (height / 4) * 3 - 90))
    
    if handPos != oHandPos and oHandPos != "":
        moveSound.play()

    if state != oState and oState != "":
        selectSound.play()

    pygame.display.flip()
    clock.tick(60)
    oHandPos = handPos
    oState = state

    # honestly couldnt care about the processing speed of the menu
    moveSound.set_volume(optionsd["svol"] / 100)
    selectSound.set_volume(optionsd["svol"] / 100)

