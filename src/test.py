import pygame
from pygame.locals import KEYDOWN, K_SPACE, K_RETURN

from random import seed, randint
from math import cos

from testing.base_pygame import init, mainloop
from testing.bad_voronoi import bad_voronoi

from classes.cell import Cell
from classes.v2 import v2

from neighbors import is_neighbor
from build_bound import find_intersections


seed(0)
def update_back():
    bad_voronoi(W, H, back, cells, colors, 4)


def gen_cells(W: int, H: int, n: int = 4):
    global cells, cells_w, colors

    cells = []
    cells_w = []
    colors = []

    for _ in range(n):
        cells.append(Cell(v2(randint(0, W-1), randint(0, H-1)),
                           randint(10, 30)*.1))
        colors.append(tuple(randint(127, 255) for _ in range(3)))

    # zoom out to better see the full circles
    zoom = .3
    offset = .5 * (1-zoom)
    for cell in cells:
        cell.pos = cell.pos*zoom + v2(W, H) * offset

        # for animating weights
        cells_w.append(cell.weight)

    update_back()


def refresh():
    if animate:
        t = cos(pygame.time.get_ticks() / 3000)*.55 + .55
        if t > 1:
            t = 1
        for cell, weight in zip(cells, cells_w):
            cell.weight = weight + (1-weight) * t

        update_back()

    screen.blit(back, (0, 0))

    for cell in cells:
        pygame.draw.circle(screen, (0, 0, 0), list(cell.pos), 5)

    neighbors = [[] for _ in range(len(cells))]
    for i, A in enumerate(cells):

        for j in range(i+1, len(cells)):
            B = cells[j]

            if is_neighbor(cells, i, j):
                pygame.draw.line(screen, (127, 127, 127), list(A.pos), list(B.pos))
                neighbors[i].append(j)
                neighbors[j].append(i)

    intersections = find_intersections(cells, neighbors)
    for inter in intersections:
        pygame.draw.circle(screen, (0, 0, 255), list(inter.pos), 3)

        b = list(inter.pos)
        for a in inter.cells:
            pygame.draw.line(screen, (255, 0, 0), list(a.pos), b)

    pygame.display.flip()


def main(events):
    global animate

    rerun = False

    for event in events:
        if event.type == KEYDOWN and event.key == K_SPACE:
            gen_cells(W, H)

            rerun = True

        # switch between weight and no weight
        if event.type == KEYDOWN and event.key == K_RETURN:
            animate = not animate
            if not animate:
                for cell, weight in zip(cells, cells_w):
                    cell.weight = weight
                update_back()

            rerun = True

    if rerun or animate:
        refresh()

cells: list[Cell] = []
cells_w: list[float] = []
colors: list[tuple] = []

animate = False

W, H, screen, font = init(1280, 720)
back = pygame.Surface((W, H))
gen_cells(W, H)

mainloop(main)
