import pygame
from pygame.locals import Rect, K_ESCAPE, QUIT, KEYDOWN, MOUSEWHEEL, MOUSEBUTTONDOWN
from pygame.math import Vector2 as v2

from math import cos, sin, atan2, ceil, tau

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
        self._range = .5
        self._angle = 0
        self.set_bounds()

    def set_bounds(self):
        self.start = self._angle-self._range
        self.stop = self._angle+self._range

    def set_params(self, start, stop):
        self.start, self.stop = start, stop

        # also update the other params needed for mouse responsiveness
        self._range = (stop-start)/2
        self._angle = (start+stop)/2

    def update(self, events):
        # change range
        for event in events:
            if event.type == MOUSEWHEEL:
                self._range += .05 * event.y

        # change rotation
        diff = pygame.mouse.get_pos()-center
        self._angle = atan2(diff.y, diff.x)
        self.set_bounds()

    def display(self):
        radius = RADIUS * (1+0.1*blocks.index(self)+displacement)

        # display range
        a0, a1 = self._angle-self._range, self._angle+self._range
        A = center + radius * v2(cos(a0), sin(a0))
        B = center + radius * v2(cos(a1), sin(a1))
        point(A)
        point(B)

        # inverted y, need to swap the angles
        v = v2(radius, radius)
        pygame.draw.arc(screen, (0, 0, 0), Rect(center-v, v*2), -a1, -a0)


def merge():
    """returns True if the circle is completely blocked, False otherwise"""

    def merge_inner():
        """returns True if merged something, False otherwise"""

        for i, block1 in enumerate(blocks):
            for j, block2 in enumerate(blocks):
                if i == j:
                    continue

                a0, a1 = block1.start, block1.stop
                b0, b1 = block2.start, block2.stop

                # shift b to be right after a in angle, to avoid modulo issues
                offset = ceil((a0-b0) / tau) * tau
                b0 += offset
                b1 += offset

                if a0 < b0 < a1:
                    # merging occurs
                    block1.set_params(a0, max(a1, b1))
                    blocks.pop(j)
                    return True

        return False

    runs = 0
    # TODO remove this
    while merge_inner():
        runs += 1
        if runs > 100:
            raise Exception("something went wrong")

    # check if the circle is entirely covered
    for block in blocks:
        if block.stop - block.start > tau:
            return True

    return False


blocks = [Block()]
colors = [
        [(127, 255, 127), (255, 192, 127)], # background
        [(63, 191, 63), (191, 127, 63)] # circle
]

done = False
run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or \
                event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False

        if event.type == MOUSEBUTTONDOWN:
            # make the last block static, and add a new one a bit further away
            if merge():
                done = True
            else:
                blocks.append(Block())

    # display circle
    screen.fill(colors[0][done])
    pygame.draw.circle(screen, colors[1][done], center, RADIUS)
    pygame.draw.circle(screen, (0, 0, 0), center, RADIUS, width=1)

    if not done:
        blocks[-1].update(events)
    for block in blocks:
        block.display()

    pygame.display.flip()
    clock.tick(60)
