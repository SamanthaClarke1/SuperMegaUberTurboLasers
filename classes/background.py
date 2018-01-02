import pygame

class Background(pygame.sprite.Sprite):

    def __init__(self, image_file, location):

        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer

        self.image = pygame.image.load(image_file)

        self.rect = self.image.get_rect()

        self.rect.left, self.rect.top, self.rect.width, self.rect.height = location

        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))