import pygame
from pygame.locals import Rect, K_ESCAPE, QUIT, KEYDOWN, MOUSEWHEEL, MOUSEBUTTONDOWN
from pygame.math import Vector2 as v2

from math import cos, sin, atan2

pygame.init()

displacement = .3

RADIUS = 100
W, H = 640, 480
center = v2(W/2, H/2)
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()


def point(pos, color=(0, 0, 0), radius=7):
    pygame.draw.circle(screen, color, pos, radius)


class Block:
    def __init__(self):
        self.range = .5
        self.angle = 0
        self.radius = RADIUS * (1+displacement)

    def update(self, events):
        # change range
        for event in events:
            if event.type == MOUSEWHEEL:
                self.range += .05 * event.y

        # change rotation
        diff = pygame.mouse.get_pos()-center
        self.angle = atan2(diff.y, diff.x)

    def display(self):
        # display range
        a0, a1 = self.angle-self.range, self.angle+self.range
        A = center + self.radius * v2(cos(a0), sin(a0))
        B = center + self.radius * v2(cos(a1), sin(a1))
        point(A)
        point(B)

        # inverted y, need to sway the angles
        v = v2(self.radius, self.radius)
        pygame.draw.arc(screen, (0, 0, 0), Rect(center-v, v*2), -a1, -a0)


blocks = [Block()]

run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or \
                event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False

        if event.type == MOUSEBUTTONDOWN:
            # make the last block static, and add a new one a bit further away
            displacement += .1
            blocks.append(Block())

    # display circle
    screen.fill((127, 255, 127))
    pygame.draw.circle(screen, (63, 191, 63), center, RADIUS)
    pygame.draw.circle(screen, (0, 0, 0), center, RADIUS, width=1)

    blocks[-1].update(events)
    for block in blocks:
        block.display()

    pygame.display.flip()
    clock.tick(60)
