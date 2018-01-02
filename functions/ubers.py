from random import randint

ubers = [
    {"type": "ball", "isDefensive": 0},
    {"type": "shield", "isDefensive": 1},
    {"type": "heal", "isDefensive": 1},
    {"type": "speed", "isDefensive": 1},
    {"type": "missile", "isDefensive": 0},
    {"type": "scatter", "isDefensive": 0},
    {"type": "sniper", "isDefensive": 0},
    {"type": "blood4bullets", "isDefensive": 0},
    {"type": "blood4flame", "isDefensive": 1},
    {"type": "blood4dust", "isDefensive": 0}
]

def get_ubers():
    return ubers

def get_defensive_ubers():
    defensiveUbers = []
    for uber in ubers:
        if uber.isDefensive == 1:
            defensiveUbers.append(uber)

    return defensiveUbers

def get_offensive_ubers():
    offensiveUbers = []
    for uber in ubers:
        if uber.isDefensive == 0:
            offensiveUbers.append(uper)

    return offensiveUbers

def get_random_uber():
    while(True):
        try:
            index = randint(0, len(ubers))
            return ubers[index]
        except:
            pass