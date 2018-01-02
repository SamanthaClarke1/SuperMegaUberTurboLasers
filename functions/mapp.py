from random import randint

mapBounds = [5500, 5500, 1]


# honestly should've made an algorithm but i cant be bothered. im tired. i mean this also technically makes my program faster lol
# format, for access, is as follows mapSectors[gridy][gridx][x or y point][start or end]

mapSectors = []
neutralSectors = []

def refresh_map_sectors():

    return      [
                    [
                        [ [0, mapBounds[0] / 3],   [0, mapBounds[1] / 3] ],
                        [ [mapBounds[0] / 3, mapBounds[0] / 3 * 2],  [0, mapBounds[1] / 3] ],
                        [ [mapBounds[0] / 3 * 2, mapBounds[0] ],   [0, mapBounds[1] / 3] ]
                    ],
                    [
                        [ [0, mapBounds[0] / 3],   [mapBounds[1] / 3, mapBounds[1] / 3 * 2] ],
                        [ [mapBounds[0] / 3, mapBounds[0] / 3 * 2],  [mapBounds[1] / 3, mapBounds[1] / 3 * 2] ],
                        [ [mapBounds[0] / 3 * 2, mapBounds[0] ],   [mapBounds[1] / 3, mapBounds[1] / 3 * 2] ]
                    ],
                    [
                        [ [0, mapBounds[0] / 3], [mapBounds[1] / 3 * 2, mapBounds[1]] ],
                        [ [mapBounds[0] / 3, mapBounds[0] / 3 * 2],   [mapBounds[1] / 3 * 2, mapBounds[1]] ],
                        [ [ mapBounds[0] / 3 * 2, mapBounds[0] ],   [mapBounds[1] / 3 * 2, mapBounds[1]] ]
                    ]
                ]

def refresh_neutral_sectors():
    return          [
                        mapSectors[0][1],
                        mapSectors[1][0],
                        mapSectors[1][1],
                        mapSectors[1][2],
                        mapSectors[2][1]
                    ]

mapSectors = refresh_map_sectors()
neutralSectors = refresh_neutral_sectors()

def translateToCam(x, y, cam):
    return x - cam[0], y - cam[1]

def teamToSector(teamNum):
    #for xsecs in mapSectors:
        #print()
        #for sec in xsecs:
            #print(sec)
    if teamNum == 1:
        return mapSectors[0][0]

    elif teamNum == 2:
        return mapSectors[2][2]

    elif teamNum == 3:
        return mapSectors[0][2]

    elif teamNum == 4:
        return mapSectors[2][0]
    
    else:
        return False

def get_sector_list():
    return mapSectors

def get_map_bounds():
    return mapBounds

def get_neutral_sectors():
    return neutralSectors

def get_player_spawn(teamnum):
    csector = teamToSector(teamnum)
    if(csector != False):
        #print(csector[0])
        #print(csector[1])
        #print()
        spawnx = randint(int(csector[0][0]), int(csector[0][1]))
        spawny = randint(int(csector[1][0]), int(csector[1][1]))
    else:
        print("teamnum " + teamnum)
        spawnx = 50
        spawny = 50

    return spawnx, spawny
