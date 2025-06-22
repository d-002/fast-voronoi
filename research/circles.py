import pygame
from pygame.locals import Rect, KEYDOWN, MOUSEBUTTONUP, K_ESCAPE, QUIT
from math import sqrt
from random import randint

from slider import Slider
from point import Point


class v2:
    def __init__(self, x, y):
        self.x, self.y = x, y


smol = 1e-9

pygame.init()

W, H = 640, 480
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 16)

sliders = []
points = []

weights = [1, .884, 2, 1.2]
pos = [(100, 400), (300, 50), (400, 250), (280, 150)]
for i in range(4):
    sliders.append(Slider(Rect(20, 20 + 30*i, 100, 30), .1, 5, chr(97+i), font,
                          weights[i]))
    points.append(Point(pos[i], chr(65+i), font))

colors = [[randint(127, 255) for _ in range(3)] for _ in range(len(points))]


def get_dot(A, B):
    return A.x*B.x + A.y*B.y


def get_closest_to_line(A, vec, P):
    """
    returns the closest point to P that is inside the line directed by vec
    and that passes through A
    """

    dap = v2(P.x-A.x, P.y-A.y)

    t = vec.x*dap.x + vec.y*dap.y

    return v2(A.x + vec.x*t, A.y + vec.y*t)


def get_middle(A, B):
    return v2((A.x+B.x) / 2, (A.y+B.y) / 2)


def get_median(A, B):
    dx, dy = B.x-A.x, B.y-A.y

    mid = get_middle(A, B)
    dab = sqrt(dx*dx + dy*dy)
    u = v2((B.y-A.y) / dab, (A.x-B.x) / dab)

    return mid, u


def get_t(M, u, P):
    """
    returns how far along the line directed by u and that passes through M,
    P is. The "origin" (t = 0) is at M, and t = 1 is at M+u.
    """

    if abs(u.x) < abs(u.y):
        return (P.y-M.y) / u.y

    return (P.x-M.x) / u.x


def get_equidistant(A, B, C):
    """
    Let (a) be the median (origin, directing vector) between A and B, and (b)
    the median between A and C
    Let X be the point equidistant to A, B and C.
    X is the intersection between (a) and (b)
    return None if the two lines are parallel, X otherwise
    """

    M, u = get_median(A, B)
    N, v = get_median(A, C)

    # handle when A, B and C are aligned
    if abs(u.x*v.y - u.y*v.x) < smol:
        return None

    # handle divisions by zero with multiple definitions of t
    if abs(v.x) < abs(v.y):
        mv = v.x/v.y
        div = u.x - mv*u.y

        # div shouldn't be zero,
        # we checked that above with colinear vectors check
        t = (N.x - M.x + mv * (M.y-N.y)) / div

    else:
        mv = v.y/v.x
        div = u.y - mv*u.x

        t = (N.y - M.y + mv * (M.x-N.x)) / div

    return v2(M.x + u.x*t, M.y + u.y*t)


def get_circle(A, B, wa, wb):
    xa, ya = A
    xb, yb = B
    wa2, wb2 = wa*wa, wb*wb

    # x polynomial
    a = wa2 - wb2
    b_x = 2 * (xb*wb2 - xa*wa2)
    c_x = wa2*xa*xa - wb2*xb*xb

    # y polynomial
    b_y = 2 * (yb*wb2 - ya*wa2)
    c_y = wa2*ya*ya - wb2*yb*yb

    # x circle equation
    alpha_x = b_x / (2*a)
    gamma_x = c_x/a - alpha_x*alpha_x

    # y circle equation
    alpha_y = b_y / (2*a)
    gamma_y = c_y/a - alpha_y*alpha_y

    r2 = -gamma_x-gamma_y
    pos = (-alpha_x, -alpha_y)

    return pos, r2


def circle_inter(ca, cb):
    # warning: the radii are already squared
    a1, b1 = ca[0]
    r1, r2 = ca[1], cb[1]
    a2, b2 = cb[0]

    # solve quadratic equation for y
    da, db = a2-a1, b1-b2
    rest = r1 - r2 + a2*a2 - a1*a1 + b2*b2 - b1*b1
    a = db*db / (da*da) + 1
    b = db*rest / (da*da) - 2*a1*db/da - 2*b1
    c = rest*rest / (4*da*da) - a1*rest/da + a1*a1 + b1*b1 - r1

    solutions = quadratic(a, b, c)

    for i in range(len(solutions)):
        y = solutions[i]
        x = (2*db*y + rest) / (2*da)

        solutions[i] = (x, y)

    return solutions


def quadratic(a, b, c):
    delta = b*b - 4*a*c
    if delta < 0:
        return []
    if delta == 0:
        return [-b / (2*a)]

    d = sqrt(delta)
    return [
            (-b - d) / (2*a),
            (-b + d) / (2*a)
    ]


def circle_inter_line(mid, vec, circle):
    x0, y0 = mid.x, mid.y
    xu, yu = vec.x, vec.y
    xc, yc = circle[0]
    r = circle[1]

    # avoid divisions by zero
    if abs(xu) < abs(yu):
        a = 1 + xu*xu/(yu*yu)
        b = (2*x0*xu - 2*xc*xu - 2*y0 * (xu*xu)/yu) / yu - 2*yc
        c = x0*x0 + xc*xc + yc*yc - r*r - 2*xc*x0 + y0*xu/yu * (2*xc - 2*x0 + y0*xu/yu)

        solutions = quadratic(a, b, c)

        return [v2(x0 + (y-y0) / yu * xu, y) for y in solutions]
    else:
        a = 1 + yu*yu/(xu*xu)
        b = (2*y0*yu - 2*yc*yu - 2*x0 * (yu*yu)/xu) / xu - 2*xc
        c = y0*y0 + xc*xc + yc*yc - r*r - 2*yc*y0 + x0*yu/xu * (2*yc - 2*y0 + x0*yu/xu)

        solutions = quadratic(a, b, c)

        return [v2(y0 + (x-x0) / xu * yu, x) for x in solutions]

def is_neighbor(i, j):
    A, B = points[i], points[j]
    wa, wb = weights[i], weights[j]
    wa = wb

    if wa == wb:
        tmin, tmax = -1e6, 1e6
        mid, vec = get_median(A, B)

        for k, P in enumerate(points):
            wp = weights[k]

            if P == A or P == B:
                continue

            if wp == wa:
                # line to line intersection

                X = get_equidistant(A, B, P)

                if X is None:
                    if get_dot(v2(P.x-A.x, P.y-A.y), v2(P.x-B.x, P.y-B.y)) < 0:
                        # P is between A and B
                        tmin = 1
                        tmax = 0
                        break
                    else:
                        continue

            else:
                # line to circle intersection

                # only need to check the intersection circle with A, since its
                # intersections with the line will be the same as with B
                # (Easily provable, even with all different weights: the
                # intersection point is along the median arc between A and B,
                # meaning we easily know the distance to A relative to B and
                # vice versa. Then, we know from the weight of C how far away
                # the point will be from it, relative to both A and B. For
                # example, if A has a higher weight (smaller circle), then the
                # intersection point will be dragged closer to it, even from C)

                circle = get_circle(A.pos, P.pos, wa, wp)
                intersections = circle_inter_line(mid, vec, circle)

                if not intersections:
                    continue

                # in case there are multiple intersections, pick the relevant
                # one
                elif len(intersections) > 2:
                    d0 = get_dist2(intersections[0], mid)
                    d1 = get_dist2(intersections[1], mid)

                    X = intersections[d1 < d0]
                else:
                    X = intersections[0]

            t = get_t(mid, vec, X)
            # get how far down the line this point is

            # get which bound is being modified by looking at
            # which side of (AB) P is
            H = get_closest_to_line(mid, vec, P)
            t_side = get_t(mid, vec, H)

            if t_side < 0:
                if t > tmin:
                    tmin = t
            else:
                if t < tmax:
                    tmax = t

        return tmax > tmin

    else:
        return False


# duplicate from test.py
def get_dist2(point, pos, weight=1):
    dx = (point.pos[0]-pos[0])*weight
    dy = (point.pos[1]-pos[1])*weight

    return dx*dx + dy*dy


def bad_voronoi(surf, points, weights, step=2):
    # draw cells
    for x in range(0, W, step):
        for y in range(0, H, step):
            min = -1
            mind = 0

            pixel = x, y
            for i, (point, weight) in enumerate(zip(points, weights)):
                d = get_dist2(point, pixel, weight)

                if d < mind or min == -1:
                    min = i
                    mind = d

            pygame.draw.rect(surf, colors[min], Rect(x, y, step, step))


voronoi_surf = pygame.Surface((W, H))
bad_voronoi(voronoi_surf, points, weights)

run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or \
                event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False

        if event.type == MOUSEBUTTONUP:
            bad_voronoi(voronoi_surf, points, weights)

    screen.blit(voronoi_surf, (0, 0))
    for s in sliders:
        s.update(events, screen)

    selected = False
    for p in points:
        selected |= p.update([] if selected else events, screen)

    # try:
    for i in range(len(points)):
        neighbors = []

        for j in range(len(points)):
            if j == i:
                continue

            # check circles intersections
            for k in range(len(points)):
                if k == i or k == j:
                    continue

                ab = get_circle(points[i].pos, points[j].pos,
                                sliders[i].get(), sliders[j].get())
                ac = get_circle(points[i].pos, points[k].pos,
                                sliders[i].get(), sliders[k].get())

                pygame.draw.circle(screen, (255, 0, 0), ab[0],
                                   sqrt(ab[1]), width=1)
                pygame.draw.circle(screen, (255, 0, 0), ac[0],
                                   sqrt(ac[1]), width=1)

                inter = circle_inter(ab, ac)
                for pos in inter:
                    pygame.draw.circle(screen, (0, 255, 0), pos, 7)

            if is_neighbor(i, j):
                neighbors.append(j)

        # display neighbors lines
        for j in neighbors:
            pygame.draw.line(screen, (0, 0, 0), points[i].pos, points[j].pos)

    # except ZeroDivisionError:
    #     screen.blit(font.render('zero div', True, (255, 0, 0)), (0, 0))

    pygame.display.flip()
    clock.tick(60)
