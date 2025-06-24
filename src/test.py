import pygame
from pygame.locals import KEYDOWN, K_SPACE

from random import randint

from testing.base_pygame import init, mainloop
from testing.bad_voronoi import bad_voronoi

from classes.cell import Cell
from classes.v2 import v2

                # todo: cache circle intersections etc at first


def gen_points(W: int, H: int, n: int = 10):
    global points, colors

    points = []
    colors = []

    for _ in range(n):
        points.append(Cell(v2(randint(0, W-1), randint(0, H-1)),
                           randint(10, 30)*.1))
        colors.append(tuple(randint(127, 255) for _ in range(3)))


def main(events):
    for event in events:
        if event.type == KEYDOWN and event.key == K_SPACE:
            gen_points(W, H)

    bad_voronoi(W, H, screen, points, colors)

    for point in points:
        pygame.draw.circle(screen, (0, 0, 0), list(point.pos), 7)


points: list[Cell] = []
colors: list[tuple] = []

W, H, screen, font = init()
gen_points(W, H)

mainloop(main)
