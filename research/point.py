import pygame
from pygame.locals import Rect, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame.math import Vector2 as v2

from slider import Slider


class Point:
    BASE_COLOR = (0, 0, 0)
    RADIUS = 7

    def __init__(self, pos, weight, i, font, color=None):
        self.pos = pos
        self.weight = weight

        if color is None:
            color = Point.BASE_COLOR
        self.color = color

        self.label = font.render(chr(65+i), True, color)

        self.rect = Rect(
            self.pos.x-Point.RADIUS,
            self.pos.y-Point.RADIUS,
            Point.RADIUS*2 + 1,
            Point.RADIUS*2 + 1)

        # point movement
        self.delta_move = None

        self.slider = Slider(Rect(20, 20 + 30*i, 100, 30), .1, 5, chr(97+i),
                             font, weight)

    def update(self, events, surf):
        """returns True if selected the point, False otherwise
        to avoid selecting multiple points at the same time"""

        # move with events
        res = False
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.prev_pos = v2(*self.pos)
                    self.delta_move = (event.pos[0]-self.pos.x,
                                       event.pos[1]-self.pos.y)
                    res = True

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                self.delta_move = None

        if self.delta_move is not None and pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            self.pos = v2(
                mx - self.delta_move[0],
                my - self.delta_move[1]
            )
            self.rect.x = self.pos.x-Point.RADIUS
            self.rect.y = self.pos.y-Point.RADIUS

        # render to screen
        # point
        pygame.draw.circle(surf, self.color, self.pos, Point.RADIUS)

        # label
        surf.blit(self.label,
                  (self.rect.right+5, self.pos.y - self.label.get_height()/2))

        # slider
        self.slider.update(events, surf)
        self.weight = self.slider.get()

        return res
