import pygame
from pygame.locals import *

class Slider:
    SLIDER_COL = (150, 150, 150)
    HANDLE_COL = (63, 63, 63)

    def __init__(self, rect, _min, _max, initial=None):
        self.rect = rect
        self.min, self.max = _min, _max
        self.active = False

        if initial is None:
            self.t = .5
        else:
            self.t = min(max((initial-_min) / (_max-_min), 0), 1)

    def get_value():
        return self.min + (self.max-self.min)*self.t

    def update(self, events, surf):
        # update value with events
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                self.active = False

        if self.active:
            mx = pygame.mouse.get_pos()[0]
            self.t = min(max((mx-self.rect.left) / self.rect.width, 0), 1)

        # render to screen
        y = (self.rect.top+self.rect.bottom)/2
        pygame.draw.rect(surf, Slider.SLIDER_COL, Rect(self.rect.left, y-2, self.rect.width, 5))

        x = self.rect.left + self.rect.width*self.t
        pygame.draw.circle(surf, Slider.HANDLE_COL, (x, y), 6)
