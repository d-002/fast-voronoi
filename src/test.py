import pygame
from pygame.locals import KEYDOWN, K_SPACE, K_RETURN

from random import seed, randint
from math import cos

from testing.base_pygame import init, mainloop
from testing.bad_voronoi import bad_voronoi

from classes.v2 import v2
from classes.cell import Cell
from classes.bounds import Bounds

from neighbors import is_neighbor
from intersections import all_intersections
from polygons import make_polygons

from time import sleep
from testing.debug import debug_show_all_blocks


def slp(t):
    sleep(t)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()


seed(0)
def update_back():
    pass#bad_voronoi(W, H, back, cells, colors, 4)


def gen_cells(W: int, H: int, n: int = 20):
    global cells, cells_w, colors

    cells = []
    cells_w = []
    colors = []

    for _ in range(n):
        cells.append(Cell(v2(randint(margin, W-margin-1),
                             randint(margin, H-margin-1)),
                           randint(10, 30)*.1))
        colors.append(tuple(randint(127, 255) for _ in range(3)))

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
    offset = 0
    for m, group in enumerate(make_polygons(bounds, cells)):
        for polygon in group:
            center = sum(polygon, start=v2(0, 0)) * (1/len(polygon))

            for i in range(len(polygon)):
                a, b = polygon[i-1], polygon[i]
                a += (center-a).normalized()*offset
                b += (center-b).normalized()*offset

                pygame.draw.line(screen, (127, 127, 127), list(a), list(b))
                #r = 255 - 255*i//len(polygon)
                #pygame.draw.line(screen, (r, 0, 255-r), list(a), list(b))
                #slp(.02)
                #pygame.display.flip()

            pygame.draw.polygon(screen, colors[m], [list(p) for p in polygon])
            #slp(.2)

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
                neighbors[i].append(j)
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

cells: list[Cell] = []
cells_w: list[float] = []
colors: list[tuple] = []

animate = False

margin = 100

W, H, screen, font = init(1280, 720)
bounds = Bounds(margin, margin, W-margin*2, H-margin*2)
back = pygame.Surface((W, H))

gen_cells(W, H)
bounds = Bounds(margin, margin-10, W-margin*2, H-margin*2)
refresh()

mainloop(main)
