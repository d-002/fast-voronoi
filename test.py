from random import randint
from math import sin

import pygame
from pygame.locals import *

from voronoi import *

# settings
N = 3 # number of cells
w, h = 1280, 720 # screen resolution
margin = 100 # box margin
box = Rect(margin, margin, w - margin*2, h - margin*2)

# pygame init
pygame.init()

clock = pygame.time.Clock()
ticks = pygame.time.get_ticks
black, white, gray = (0,)*3, (255,)*3, (127,)*3

screen = pygame.display.set_mode((w, h))

# display stuff
_r = lambda: randint(127, 255)
def rand_col():
    return _r(), _r(), _r()

def display(points, points_cols, neighbors, polygons):
    for i, polygon in enumerate(polygons):
        pygame.draw.polygon(screen, points_cols[i], [p.to_tuple() for p in polygon])

    mul = 1
    for i, polygon in enumerate(polygons):
        A = points[i]
        _p = [None]*len(polygon)

        for j in range(len(polygon)):
            B = polygon[j]
            _p[j] = (A.x + (B.x-A.x)*mul, A.y + (B.y-A.y)*mul)

        pygame.draw.lines(screen, black, True, _p)

    for i in range(N):
        for j in neighbors[i]:
            pygame.draw.line(screen, gray, points[i].to_tuple(), points[j].to_tuple())

    for A in points:
        pygame.draw.rect(screen, black, Rect(A.x-1, A.y-1, 3, 3))

def bad_voronoi(points, step=2):
    # cache cells colors
    colors = [rand_col() for _ in range(len(points))]

    # draw cells
    for x in range(0, w, step):
        for y in range(0, h, step):
            min = None
            mind = 0

            pixel = (x, y)
            for i, point in enumerate(points):
                d = get_dist2(point, pixel)

                if d < mind or min is None:
                    min = i
                    mind = d

            pygame.draw.rect(screen, colors[min], Rect(x, y, step, step))

    pygame.display.flip()

def make_points():
    points = [Point(randint(box.left, box.right), randint(box.top, box.bottom)) for _ in range(N)]
    remove_collisions(points)
    points_cols = [rand_col() for _ in range(len(points))]

    return points, points_cols

# update function: display voronoi diagram with random points
def run(points, points_cols):
    neighbors, polygons = make_polygons(points, box)

    screen.fill(white)

    # naive approach
    #bad_voronoi(points, 1)
    # polygon approach
    display(points, points_cols, neighbors, polygons)

# main loops
def perf_demo():
    """runs the selected approach multiple times, either on click or every frame"""

    run(*make_points())

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                if event.key == K_SPACE:
                    run(*make_points())

        #run(*make_points())

        pygame.display.flip()
        clock.tick(10)

def weight_demo():
    """make the cells weights change a bit over time"""

    points, points_cols = make_points()

    t0 = ticks()
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return

        # edit points weights
        run(points, points_cols)

        pygame.display.flip()
        clock.tick(60)

perf_demo()
#weight_demo()
