import pygame
from pygame.locals import *

from slider import *
from point import *

pygame.init()

screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 16)

sliders = [
    Slider(Rect(20, 20, 100, 30), .1, 5, 'a', font, 1),
    Slider(Rect(20, 50, 100, 30), .1, 5, 'b', font, 2),
    Slider(Rect(20, 80, 100, 30), .1, 5, 'c', font, .5)
]

points = [
    Point((100, 400), 'A', font),
    Point((300, 50), 'B', font),
    Point((500, 150), 'C', font)
]

def get_circle(A, B, wa, wb):
    xa, ya = A
    xb, yb = B
    wa2, wb2 = wa*wa, wb*wb

    # x polynomial
    a = wb2 - wa2
    b_x = 2 * (xb*wa2 - xa*wb2)
    c_x = wb2*xa*xa - wa2*xb*xb

    # y polynomial
    b_y = 2 * (yb*wa2 - ya*wb2)
    c_y = wb2*ya*ya - wa2*yb*yb

    # x circle equation
    mu = a
    alpha_x = b_x / (2*a)
    gamma_x = c_x/a - alpha_x*alpha_x

    # y circle equation
    alpha_y = b_y / (2*a)
    gamma_y = c_y/a - alpha_y*alpha_y

    r2 = -gamma_x-gamma_y
    pos = (-alpha_x, -alpha_y)

    return pos, r2

def get_inter(ca, cb):
    return []

run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False

    screen.fill((255, 255, 255))
    for s in sliders:
        s.update(events, screen)

    selected = False
    for p in points:
        selected |= p.update([] if selected else events, screen)

    try:
        ab = get_circle(points[0].pos, points[1].pos,
                        sliders[0].get(), sliders[1].get())
        ac = get_circle(points[0].pos, points[2].pos,
                        sliders[0].get(), sliders[2].get())

        inter = get_inter(ab, ac)
        for pos in inter:
            pygame.draw.circle(screen, (255, 0, 0), pos, 6)
    except ZeroDivisionError:
        screen.blit(font.render('zero div', True, (255, 0, 0)), (0, 0))

    pygame.display.flip()
    clock.tick(60)
