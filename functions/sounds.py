import pygame
import os

_sound_library = {}

def get_sound(path):
    global _sound_library
    sound = _sound_library.get(path)
    if sound == None:
        canon_path = path.replace('/', os.sep).replace('\\', os.sep)
        sound = pygame.mixer.Sound(canon_path)
        _sound_library[path] = sound

    return sound
