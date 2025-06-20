import pygame
from pygame.locals import *
from math import sqrt

from slider import *
from point import *

pygame.init()

screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 16)

sliders = []
points = []

weights = [1, 2, .5, .8]
pos = [(100, 400), (300, 50), (500, 150), (250, 100)]
for i in range(4):
    sliders.append(Slider(Rect(20, 20 + 30*i, 100, 30), .1, 5, chr(97+i), font, weights[i]))
    points.append(Point(pos[i], chr(65+i), font))

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
    # warning: the radii are already squared
    a1, b1 = ca[0]
    r1, r2 = ca[1], cb[1]
    a2, b2 = cb[0]

    # solve quadratic equation for y
    da, db = a2-a1, b1-b2
    I = r1 - r2 + a2*a2 - a1*a1 + b2*b2 - b1*b1
    a = db*db / (da*da) + 1
    b = db*I / (da*da) - 2*a1*db/da - 2*b1
    c = I*I / (4*da*da) - a1*I/da + a1*a1 + b1*b1 - r1

    delta = b*b - 4*a*c
    if delta < 0:
        solutions = []
    elif delta:
        d = sqrt(delta)

        solutions = [
            (-b-d) / (2*a),
            (-b+d) / (2*a)
        ]
    else:
        solutions = [-b/(2*a)]

    for i in range(len(solutions)):
        y = solutions[i]

        x = (2*db*y + I) / (2*da)

        solutions[i] = (x, y)

    return solutions

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
        for i in range(len(points)):
            for j in range(len(points)):
                if j == i: continue

                for k in range(len(points)):
                    if k == i or k == j: continue

                    ab = get_circle(points[i].pos, points[j].pos,
                                    sliders[i].get(), sliders[j].get())
                    ac = get_circle(points[i].pos, points[k].pos,
                                    sliders[i].get(), sliders[k].get())

                    pygame.draw.circle(screen, (255, 0, 0), ab[0], sqrt(ab[1]), width=1)
                    pygame.draw.circle(screen, (255, 0, 0), ac[0], sqrt(ac[1]), width=1)

                    inter = get_inter(ab, ac)
                    for pos in inter:
                        pygame.draw.circle(screen, (0, 255, 0), pos, 7)
    except ZeroDivisionError:
        screen.blit(font.render('zero div', True, (255, 0, 0)), (0, 0))

    pygame.display.flip()
    clock.tick(60)
