import pygame
from pygame.locals import *

class Slider:
    SLIDER_COL = (150, 150, 150)
    HANDLE_COL = (63, 63, 63)

    def __init__(self, rect, _min, _max, label, font, initial=None):
        self.rect = rect
        self.min, self.max = _min, _max

        self.label = label
        self.font = font

        self.active = False

        if initial is None:
            self.t = .5
        else:
            self.t = min(max((initial-_min) / (_max-_min), 0), 1)

    def get(self):
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
        # slider
        y = (self.rect.top+self.rect.bottom)/2
        pygame.draw.rect(surf, Slider.SLIDER_COL, Rect(self.rect.left, y-2, self.rect.width, 5))

        # handle
        x = self.rect.left + self.rect.width*self.t
        pygame.draw.circle(surf, Slider.HANDLE_COL, (x, y), 6)

        # label
        label = self.font.render(
            "%s = %.3f" %(self.label, self.get()),
            True,
            Slider.HANDLE_COL)
        surf.blit(label, (self.rect.right+10, self.rect.top + (self.rect.height-label.get_height())/2))
