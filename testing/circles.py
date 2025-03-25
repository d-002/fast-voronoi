import pygame
from pygame.locals import *

from slider import *
from point import *

pygame.init()

screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 16)

a = Slider(Rect(20, 20, 100, 30), .1, 5, 'a', font)
b = Slider(Rect(20, 50, 100, 30), .1, 5, 'b', font)

points = [
    Point((100, 300), 'A', font),
    Point((400, 200), 'B', font)
]

def get_polynomial(A, B):
    return 0

run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False

    screen.fill((255, 255, 255))
    a.update(events, screen)
    b.update(events, screen)

    selected = False
    for p in points:
        selected |= p.update([] if selected else events, screen)

    pygame.display.flip()
    clock.tick(60)
