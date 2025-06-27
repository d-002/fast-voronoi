import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
clock = pygame.time.Clock()

from math import sqrt

from neighbors import *
from classes.cell import Cell
from classes.line import Line
from classes.circle import Circle
from classes.bounds import Bounds
from classes.block_manager import StraightBlockManager, CircleBlockManager

def slp():
    pygame.display.flip()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == QUIT or \
                    event.type == KEYDOWN and event.key == K_ESCAPE:

                pygame.quit()
                exit()

            elif event.type == KEYDOWN:
                run = False

            clock.tick(10)

def draw_line(screen: pygame.Surface, color: tuple[int, int, int], line: Line):
    pygame.draw.line(screen, color,
                     list(line.M - line.u*100),
                     list(line.M + line.u*200))

def draw_circle(screen: pygame.Surface, color: tuple[int, int, int],
                circle: Circle):

    pygame.draw.circle(screen, color, list(circle.c), sqrt(circle.r2),
                       width=1)

def draw_cell(screen: pygame.Surface, cell: Cell, i: int):
    c = 63 * i + (i == 2)
    pygame.draw.circle(screen, (c, c, c), list(cell.pos), 7)

def show_straightblock(screen: pygame.Surface, line: Line,
                       manager: StraightBlockManager):
    for start, stop in manager.blocks:
        pygame.draw.line(screen, (255, 127, 0),
                         list(line.M + line.u * start),
                         list(line.M + line.u * stop))

def show_circleblock(screen: pygame.Surface, circle: Circle,
                     manager: CircleBlockManager):

    offset = v2(1, 1) * sqrt(circle.r2)

    # invert angles since the viewport is flipped in pygame
    for a1, a2 in manager.blocks:
        a1, a2 = -a2, -a1

        pygame.draw.arc(screen, (255, 127, 0),
                        pygame.Rect(list(circle.c-offset), list(offset*2)),
                        a1, a2)

def debug_show_blocks(bounds: Bounds, screen: pygame.Surface,
                      cells: list[Cell], i: int, j: int):
    A, B = cells[i], cells[j]
    draw_cell(screen, A, 0)
    draw_cell(screen, B, 1)
    pygame.draw.line(screen, (0, 255, 0), list(A.pos), list(B.pos))

    if abs(A.weight - B.weight) < smol:
        line1 = perp_bisector(A.pos, B.pos)
        manager = StraightBlockManager(line1, bounds)

        draw_line(screen, (0, 255, 0), line1)

        pygame.display.flip()
        slp()

        for k, P in enumerate(cells):
            if i == k or j == k:
                continue

            pygame.draw.line(screen, (255, 0, 0), list(A.pos), list(P.pos))
            draw_cell(screen, P, 2)
            slp()

            if abs(A.weight - P.weight) < smol:
                line2 = perp_bisector(A.pos, P.pos)
                draw_line(screen, (255, 0, 0), line2)

                if cut_line_line(A, B, P, line1, manager):
                    pass

            else:
                circle2 = get_circle(A, P)
                draw_circle(screen, (255, 0, 0), circle2)

                if cut_line_circle(A, P, line1, manager):
                    pass

            slp()
            show_straightblock(screen, line1, manager)
            slp()

    else:
        if A.weight < B.weight:
            A, B = B, A

        circle1 = get_circle(A, B)
        manager = CircleBlockManager()
        cut_circle_bounds(circle1, bounds, manager)

        draw_circle(screen, (0, 255, 0), circle1)
        show_circleblock(screen, circle1, manager)

        pygame.display.flip()
        slp()

        for k, P in enumerate(cells):
            if i == k or j == k:
                continue

            pygame.draw.line(screen, (255, 0, 0), list(A.pos), list(P.pos))
            draw_cell(screen, P, 2)
            slp()

            if abs(A.weight - P.weight) < smol:
                line2 = perp_bisector(A.pos, P.pos)
                draw_line(screen, (255, 0, 0), line2)

                # show additional info on contact points
                intersections = circle_inter_line(line2, circle1)

                if len(intersections) == 2:
                    i1, i2 = intersections
                    pygame.draw.circle(screen, (0, 0, 255), list(i2), 3)
                    pygame.draw.circle(screen, (0, 127, 255), list(i1), 3)

                    da = intersections[0]-circle1.c
                    db = intersections[1]-circle1.c
                    a_a = atan2(da.y, da.x)
                    a_b = atan2(db.y, db.x)

                    if a_b < a_a:
                        a_b += tau

                    a_mid = (a_a+a_b) / 2
                    test_point = line2.M + v2(cos(a_mid), sin(a_mid)) * 100
                    pygame.draw.circle(screen, (255, 0, 255), list(test_point), 5)

                if cut_circle_line(A, P, circle1, manager):
                    pass

                slp()
                show_circleblock(screen, circle1, manager)
                slp()

            else:
                circle2 = get_circle(A, P)
                draw_circle(screen, (255, 0, 0), circle2)

                if cut_circle_circle(A, P, circle1, manager):
                    pass

def debug_show_all_blocks(bounds: Bounds, screen: pygame.Surface,
                          cells: list[Cell]):

    prev = pygame.Surface(screen.get_size())
    prev.blit(screen, (0, 0))

    for i in range(len(cells)):
        for j in range(len(cells)):
            if i == j:
                continue

            debug_show_blocks(bounds, screen, cells, i, j)

            screen.blit(prev, (0, 0))
