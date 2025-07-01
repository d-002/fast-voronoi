import pygame
from pygame.locals import Rect

from utils import get_dist2
from classes.v2 import v2
from classes.cell import Cell


def bad_voronoi(W: int, H: int, surf: pygame.Surface, points: list[Cell],
                colors: list[tuple], step: int = 2):
    """
    Slow, intuitive approach to displaying a weighted voronoi diagram
    """

    # draw cells
    offset = step*.5
    for x in range(0, W, step):
        for y in range(0, H, step):
            min = -1
            mind = 0

            pixel = v2(x+offset, y+offset)
            for i, point in enumerate(points):
                d = get_dist2(point.pos, pixel, point.weight)

                if d < mind or min == -1:
                    min = i
                    mind = d

            # find and lighten the color
            r, g, b = colors[min]
            col = ((r+255) / 2, (g+255) / 2, (b+255) / 2)
            pygame.draw.rect(surf, col, Rect(x, y, step, step))
