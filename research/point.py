import pygame
from pygame.locals import *

class Point:
    BASE_COLOR = (0, 0, 0)
    RADIUS = 7

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

        # point movement
        self.delta_move = None

    def update(self, events, surf):
        """returns True if selected the point, False otherwise
        to avoid selecting multiple points at the same time"""

        # move with events
        res = False
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.prev_pos = tuple(self.pos)
                    self.delta_move = (event.pos[0]-self.pos[0],
                                   event.pos[1]-self.pos[1])
                    res = True

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                self.delta_move = None

        if self.delta_move is not None and pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            self.pos = (
                mx - self.delta_move[0],
                my - self.delta_move[1]
            )
            self.rect.x = self.pos[0]-Point.RADIUS
            self.rect.y = self.pos[1]-Point.RADIUS

        # render to screen
        # point
        pygame.draw.circle(surf, self.color, self.pos, Point.RADIUS)

        # label
        surf.blit(self.label, (self.rect.right+5, self.pos[1] - self.label.get_height()/2))

        return res
