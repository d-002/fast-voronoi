import pygame
from pygame.locals import *

from slider import *

screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

a = Slider(Rect(20, 20, 100, 30), .1, 5)
b = Slider(Rect(20, 50, 100, 30), .1, 5)

run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False

    screen.fill((255, 255, 255))
    a.update(events, screen)
    b.update(events, screen)

    pygame.display.flip()
    clock.tick(60)
