from random import random, randint
from math import sin

import pygame
from pygame.locals import *

from voronoi import *

# settings
N = 5 # number of cells
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
        pygame.draw.polygon(screen, points_cols[i],
                            [p.to_tuple() for p in polygon])

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
            pygame.draw.line(screen, gray,
                             points[i].to_tuple(),
                             points[j].to_tuple())

    for A in points:
        pygame.draw.rect(screen, black, Rect(A.x-1, A.y-1, 3, 3))

def bad_voronoi(points, box, step=2):
    # cache cells colors
    colors = [rand_col() for _ in range(len(points))]

    # draw cells
    for x in range(box.left, box.right, step):
        for y in range(box.top, box.bottom, step):
            min = -1
            mind = 0

            pixel = v2(x, y)
            for i, point in enumerate(points):
                d = get_dist2(point, pixel)

                if d < mind or min == -1:
                    min = i
                    mind = d

            pygame.draw.rect(screen, colors[min], Rect(x, y, step, step))

    pygame.display.flip()

def remove_collisions(points):
    """
    ugly, but needed in case some points are in the same place
    """

    N = len(points)
    while True:
        ok = True

        for i in range(N):
            for j in range(N):
                if i == j:
                    continue

                if points[i] == points[j]:
                    points[j].x += 1e-3
                    ok = False

        if ok:
            return

def make_points():
    points = [Point(randint(box.left, box.right), randint(box.top, box.bottom))
              for _ in range(N)]
    points = [
        Point(200, 200),
        Point(200, 520),
        Point(640, 360),
        Point(1080, 200),
        Point(1080, 520)
    ]
    remove_collisions(points)
    points_cols = [rand_col() for _ in range(len(points))]

    return points, points_cols

# update function: display voronoi diagram with random points
def run(points, points_cols):
    screen.fill(white)

    # naive approach
    #bad_voronoi(points, box, 1)

    # polygon approach
    neighbors, polygons = make_polygons(points, box)
    display(points, points_cols, neighbors, polygons)

# main loops
def perf_demo():
    """
    runs the selected approach multiple times, either on click or every frame
    """

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
    """
    make the cells' weights change a bit over time
    """

    # I don't care how ugly this is
    points = points_cols = target_weights = None
    def init():
        nonlocal points, points_cols, target_weights
        points, points_cols = make_points()
        target_weights = [1 + random()*5 for _ in range(N)]

    init()

    start = ticks()
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                if event.key == K_SPACE:
                    init()

        # edit points weights
        t = sin((ticks()-start) / 1000)
        t = (t+1) / 2

        for point, weight in zip(points, target_weights):
            point.weight = 1 + (weight-1) * t

        # refresh visuals
        run(points, points_cols)

        pygame.display.flip()
        clock.tick(60)

#perf_demo()
weight_demo()
