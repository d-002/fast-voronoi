import pygame
from pygame.locals import Rect, KEYDOWN, MOUSEWHEEL, K_ESCAPE, QUIT
from pygame.math import Vector2 as v2

from math import cos, sin, atan2

_range = 1
angle = .5

pygame.init()

RADIUS = 120
W, H = 640, 480
center = v2(W/2, H/2)
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()


def point(pos, color=(0, 0, 0), radius=7):
    pygame.draw.circle(screen, color, pos, radius)


run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or \
                event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False

        # change range
        if event.type == MOUSEWHEEL:
            _range += .05 * event.y

    # change rotation
    diff = pygame.mouse.get_pos()-center
    angle = atan2(diff.y, diff.x)

    screen.fill((127, 255, 127))
    pygame.draw.circle(screen, (63, 191, 63), center, RADIUS)
    pygame.draw.circle(screen, (0, 0, 0), center, RADIUS, width=1)

    # display range
    angle0, angle1 = angle-_range, angle+_range
    A = center + RADIUS*1.5 * v2(cos(angle0), sin(angle0))
    B = center + RADIUS*1.5 * v2(cos(angle1), sin(angle1))
    point(A)
    point(B)
    # inverted y, need to sway the angles
    v = v2(RADIUS*1.5, RADIUS*1.5)
    pygame.draw.arc(screen, (0, 0, 0), Rect(center-v, v*2), -angle1, -angle0)

    pygame.display.flip()
    clock.tick(60)
