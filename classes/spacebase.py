import math
from functions import images
import pygame

class SpaceBase:

  def __init__(self, Pos):
    self.xPos = Pos[0]
    self.yPos = Pos[1]
    self.width = Pos[2]
    self.height = Pos[3]
    self.img = images.get_image("data/img/spacestation.png")
    self.ang = 90
    self.rotationSpeed = .09
    self.r = ((self.width + self.height) / 2) / 2

    self.healingCapacity = 0.7
    self.maxHealingCapacity = 0.75
    self.minHealingCapacity = 0.1

    self.pulser = 0
    self.pulsecolor = (255, 255, 255, 80)
    self.pulseteam = 0

    self.maxHeaGiveout = 5

  def get_draw_pos(self, cam):
    return (self.xPos - cam[0] - self.width / 2, self.yPos - cam[1] - self.width / 2)

  def hasHealed(self):
    self.healingCapacity -= 0.0065

  def scale_image(self, img):
    return pygame.transform.scale(img, (self.width, self.height))
  
  def get_wh(self):
    return(self.width, self.height)

  def tick(self):
    self.healingCapacity += 0.004
    if self.healingCapacity > self.maxHealingCapacity:
      self.healingCapacity = self.maxHealingCapacity
    if self.healingCapacity < self.minHealingCapacity:
      self.healingCapacity = self.minHealingCapacity

    self.ang += self.rotationSpeed

    self.pulser += 1.25
    if self.pulser >= self.r * 1.2:
        self.pulser = 0

  def show(self, screen, cam):

    self.nimg = images.rot_center(self.img, self.ang)
    self.nimg = self.scale_image(self.nimg)
    screen.blit(self.nimg, self.get_draw_pos(cam))

    #pygame.draw.circle(Surface, color, pos, radius, width=0) -> Rect
    # pulsing circle
    circlepos = (int(self.xPos - cam[0]), int(self.yPos - cam[1]))
    rwidth = 8
    if rwidth > self.pulser: rwidth = self.pulser - 0.01
    pygame.draw.circle(screen, self.pulsecolor, circlepos, int(self.pulser), int(rwidth))

    # healing capacity bar
    Pos = (self.xPos - cam[0] - 50, self.yPos - cam[1] + self.r + 20)
    width = self.healingCapacity / self.maxHealingCapacity * 100
    color = (120, 255, 120)
    pygame.draw.rect(screen, color, pygame.Rect(Pos[0], Pos[1], width, 12)) 
    
  def isTouchingCircle(self, Pos, r):
    dist = math.hypot(self.xPos - Pos[0], self.yPos - Pos[1])

    if dist <= abs(r / 2) + abs(self.r / 1.8):
        return True
    return False




def abs(num):
    if num >= 0: return num
    else: return num * -1

