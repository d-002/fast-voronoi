import pygame
from pygame.locals import *

class Point:
    BASE_COLOR = (0, 0, 0)
    RADIUS = 6

    def __init__(self, pos, label, font, color=None):
        self.pos = pos

        if color is None: color = Point.BASE_COLOR
        self.color = color

        self.label = font.render(label, True, color)

        self.rect = Rect(
            self.pos[0]-Point.RADIUS,
            self.pos[1]-Point.RADIUS,
            Point.RADIUS*2 + 1,
            Point.RADIUS*2 + 1)

    def update(self, events, surf):
        """returns True if selected the point, False otherwise
        to avoid selecting multiple points at the same time"""

        # move with events
        res = False
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                pass
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                pass

        # render to screen
        # point
        pygame.draw.circle(surf, self.color, self.pos, Point.RADIUS)

        # label
        surf.blit(self.label, (self.rect.right+2, self.pos[1] - self.label.get_height()/2))

        return res
