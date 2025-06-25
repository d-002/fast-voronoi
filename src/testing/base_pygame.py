import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT

def init(_W: int = 640, _H: int = 480, _fps: int = 60) \
        -> tuple[int, int, pygame.Surface, pygame.font.Font]:
    global W, H, fps, screen, clock, font

    W, H = _W, _H
    fps = _fps

    pygame.init()

    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('consolas', 12)

    return (W, H, screen, font)

def mainloop(f):
    run = True

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT or \
                    event.type == KEYDOWN and event.key == K_ESCAPE:
                run = False

        f(events)

        clock.tick(fps)
