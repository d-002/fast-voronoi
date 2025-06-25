import pygame
from pygame.locals import KEYDOWN, K_SPACE

from random import seed, randint

from testing.base_pygame import init, mainloop
from testing.bad_voronoi import bad_voronoi

from classes.cell import Cell
from classes.v2 import v2

from neighbors import is_neighbor


def gen_cells(W: int, H: int, n: int = 4):
    global cells, colors

    cells = []
    colors = []

    for _ in range(n):
        cells.append(Cell(v2(randint(0, W-1), randint(0, H-1)),
                           randint(10, 30)*.1))
        colors.append(tuple(randint(127, 255) for _ in range(3)))

    # zoom out to better see the full circles
    for c in cells:
        c.pos = c.pos*.2 + v2(W*.4, H*.4)


seed(0)
def main(events):
    for event in events:
        if event.type == KEYDOWN and event.key == K_SPACE:
            gen_cells(W, H)

    bad_voronoi(W, H, screen, cells, colors)

    for cell in cells:
        pygame.draw.circle(screen, (0, 0, 0), list(cell.pos), 7)

    for i, A in enumerate(cells):
        for j in range(i+1, len(cells)):
            B = cells[j]

            if is_neighbor(cells, i, j):
                pygame.draw.line(screen, (0, 0, 0), list(A.pos), list(B.pos))


cells: list[Cell] = []
colors: list[tuple] = []

W, H, screen, font = init()
gen_cells(W, H)

mainloop(main)
