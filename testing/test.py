import pygame
from pygame.locals import KEYDOWN, K_SPACE, K_RETURN

from random import seed, randint
from math import cos

from base_pygame import init, mainloop
from bad_voronoi import bad_voronoi
from rand_colors import rand_colors

from fast_voronoi import v2, Cell, Bounds, Options
from fast_voronoi.neighbors import is_neighbor
from fast_voronoi.intersections import all_intersections
from fast_voronoi.polygons import make_polygons

seed(0)


def update_back():
    bad_voronoi(W, H, back, cells, colors, 4)


def gen_cells(W: int, H: int, n: int = 20):
    global cells, cells_w, colors

    cells = []
    cells_w = []
    colors = rand_colors(n)

    for _ in range(n):
        cells.append(Cell(v2(randint(margin, W-margin-1),
                             randint(margin, H-margin-1)),
                          randint(10, 30)*.1))

    # zoom out to better see the full circles
    zoom = 1
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

    # background
    screen.blit(back, (0, 0))

    # draw polygons
    for m, polygon in make_polygons(options, bounds, cells):
        pygame.draw.polygon(screen, colors[m], [list(p) for p in polygon])

    # draw bounds
    pygame.draw.line(screen, (127, 127, 127), list(bounds.tl), list(bounds.tr))
    pygame.draw.line(screen, (127, 127, 127), list(bounds.tr), list(bounds.br))
    pygame.draw.line(screen, (127, 127, 127), list(bounds.bl), list(bounds.br))
    pygame.draw.line(screen, (127, 127, 127), list(bounds.tl), list(bounds.bl))

    # cells centers
    for cell in cells:
        pygame.draw.circle(screen, (0, 0, 0), list(cell.pos), 5)

    # neighbor lines
    neighbors = [[] for _ in range(len(cells))]
    for i in range(len(cells)):
        for j in range(i+1, len(cells)):
            if is_neighbor(bounds, cells, i, j):
                pygame.draw.line(screen, (0, 255, 0),
                                 list(cells[i].pos),
                                 list(cells[j].pos))
                neighbors[j].append(i)

    # intersection points
    intersections, _ = all_intersections(bounds, cells, neighbors)
    for inter in intersections:
        pygame.draw.circle(screen, (0, 0, 255), list(inter.pos), 3)

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


options = Options()

cells: list[Cell] = []
cells_w: list[float] = []
colors: list[tuple] = []

animate = False

margin = 100

W, H, screen, font = init(1280, 720)
bounds = Bounds(margin, margin, W-margin*2, H-margin*2)
back = pygame.Surface((W, H))

gen_cells(W, H)
refresh()

mainloop(main)
