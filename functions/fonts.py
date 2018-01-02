import pygame

def rend_onlygoodfont(size, text, color):
    tfont = pygame.font.Font("data/font/PressStart2P.ttf", size)
    return tfont.render(text, True, color)
