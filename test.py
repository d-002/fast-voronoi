from random import randint

import pygame
from pygame.locals import *

from voronoi import *

# settings
N = 30 # number of cells
w, h = 1280, 720 # screen resolution
margin = 100 # box margin
box = Rect(margin, margin, w - margin*2, h - margin*2)

# pygame init
pygame.init()

clock = pygame.time.Clock()
black, white, gray = (0,)*3, (255,)*3, (127,)*3

screen = pygame.display.set_mode((w, h))

# display stuff
_r = lambda: randint(127, 255)
def rand_col():
    return _r(), _r(), _r()

def display(points, neighbors, polygons):
    for p in polygons:
        pygame.draw.polygon(screen, rand_col(), p)

    mul = 1
    for i, p in enumerate(polygons):
        x1, y1 = points[i]
        _p = [None]*len(p)

        for j in range(len(p)):
            x2, y2 = p[j]
            _p[j] = (x1 + (x2-x1)*mul, y1 + (y2-y1)*mul)

        pygame.draw.lines(screen, black, True, _p)

    for i in range(N):
        for j in neighbors[i]:
            pygame.draw.line(screen, gray, points[i], points[j])

    for x, y in points:
        pygame.draw.rect(screen, black, Rect(x-1, y-1, 3, 3))

def bad_voronoi(points, step=2):
    # cache cells colors
    colors = [rand_col() for _ in range(len(points))]

    # draw cells
    for x in range(0, w, step):
        for y in range(0, h, step):
            min = None
            mind = 0

            for i, pos in enumerate(points):
                dx, dy = pos[0]-x, pos[1]-y
                d = dx*dx + dy*dy

                if d < mind or min is None:
                    min = i
                    mind = d

            pygame.draw.rect(screen, colors[min], Rect(x, y, step, step))

    pygame.display.flip()

# update function: display voronoi diagram with random points
def run():
    points = [(randint(box.left, box.right), randint(box.top, box.bottom)) for _ in range(N)]
    remove_collisions(points)

    neighbors, polygons = make_polygons(points, box)

    screen.fill(white)

    # naive approach
    #bad_voronoi(points, 1)
    # polygon approach
    display(points, neighbors, polygons)

# main loop
def main():
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return

        # random demo multiple times
        #clock.tick(10)
        run()

        pygame.display.flip()

main()
