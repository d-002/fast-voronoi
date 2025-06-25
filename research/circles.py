import pygame
from pygame.locals import Rect, KEYDOWN, MOUSEBUTTONUP, K_ESCAPE, QUIT
from pygame.math import Vector2 as v2

from math import sqrt, cos, sin, atan2, tau
from random import seed, randint

from point import Point
from block_manager import StraightBlockManager, CircleBlockManager

def gen_points(n: int = 4):
    global points, colors

    points = []
    colors = []

    for i in range(n):
        points.append(Point(v2(randint(0, W-1), randint(0, H-1)),
                           randint(10, 30)*.1, i, font))
        colors.append(tuple(randint(127, 255) for _ in range(3)))

smol = 1e-9

pygame.init()

W, H = 640, 480
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 16)

points: list[Point] = []
colors: list[tuple] = []

seed(0)
gen_points()

def get_dot(A: v2, B: v2):
    return A.x*B.x + A.y*B.y


def get_closest_to_line(A: v2, vec: v2, P: v2):
    """
    returns the closest point to P that is inside the line directed by vec
    and that passes through A
    """

    dap = v2(P.x-A.x, P.y-A.y)

    t = vec.x*dap.x + vec.y*dap.y

    return v2(A.x + vec.x*t, A.y + vec.y*t)


def get_middle(A: v2, B: v2):
    return v2((A.x+B.x) / 2, (A.y+B.y) / 2)


def get_median(A: v2, B: v2):
    dx, dy = B.x-A.x, B.y-A.y

    mid = get_middle(A, B)
    dab = sqrt(dx*dx + dy*dy)
    u = v2((B.y-A.y) / dab, (A.x-B.x) / dab)

    return mid, u


def get_t(M: v2, u: v2, P: v2):
    """
    returns how far along the line directed by u and that passes through M,
    P is. The "origin" (t = 0) is at M, and t = 1 is at M+u.
    """

    if abs(u.x) < abs(u.y):
        return (P.y-M.y) / u.y

    return (P.x-M.x) / u.x


def get_equidistant(A: v2, B: v2, C: v2):
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


def get_circle(A: Point, B: Point):
    xa, ya = A.pos.x, A.pos.y
    xb, yb = B.pos.x, B.pos.y
    wa2, wb2 = A.weight*A.weight, B.weight*B.weight

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
    pos = v2(-alpha_x, -alpha_y)

    return pos, r2


def circle_inter(ca: tuple, cb: tuple):
    # warning: the radii are already squared
    a1, b1 = ca[0]
    r1, r2 = ca[1], cb[1]
    a2, b2 = cb[0]

    da, db = a2-a1, b1-b2

    # avoid divisions by zero
    if abs(da) < abs(db):
        rest = r1 - r2 + a2*a2 - a1*a1 + b2*b2 - b1*b1
        a = 1 + da*da / (db*db)
        b = -da*rest / (db*db) - 2*b1*da/db - 2*a1
        c = rest*rest / (4*db*db) + b1*rest/db + a1*a1 + b1*b1 - r1

        solutions = quadratic(a, b, c)

        return [v2(x, (2*da*x - rest) / (2*db)) for x in solutions]

    rest = r1 - r2 + a2*a2 - a1*a1 + b2*b2 - b1*b1
    a = 1 + db*db / (da*da)
    b = db*rest / (da*da) - 2*a1*db/da - 2*b1
    c = rest*rest / (4*da*da) - a1*rest/da + a1*a1 + b1*b1 - r1

    solutions = quadratic(a, b, c)

    return [v2((2*db*y + rest) / (2*da), y) for y in solutions]


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


def circle_inter_line(mid: v2, vec: v2, circle: tuple):
    x0, y0 = mid.x, mid.y
    xu, yu = vec.x, vec.y
    xc, yc = circle[0]
    r2 = circle[1]  # todo: use a custom data structure for circle, to indicate the radius is squared already

    # avoid divisions by zero
    if abs(xu) < abs(yu):
        a = 1 + xu*xu/(yu*yu)
        b = (2*x0*xu - 2*xc*xu - 2*y0 * (xu*xu)/yu) / yu - 2*yc
        c = x0*x0 + xc*xc + yc*yc - r2 - 2*xc*x0 + y0*xu/yu * (2*xc - 2*x0 + y0*xu/yu)

        solutions = quadratic(a, b, c)

        return [v2(x0 + (y-y0) / yu * xu, y) for y in solutions]

    a = 1 + yu*yu/(xu*xu)
    b = (2*y0*yu - 2*yc*yu - 2*x0 * (yu*yu)/xu) / xu - 2*xc
    c = y0*y0 + xc*xc + yc*yc - r2 - 2*yc*y0 + x0*yu/xu * (2*yc - 2*y0 + x0*yu/xu)

    solutions = quadratic(a, b, c)

    return [v2(x, y0 + (x-x0) / xu * yu) for x in solutions]

def is_neighbor(i: int, j: int):
    A, B = points[i], points[j]

    if abs(A.weight-B.weight) < smol:
        mid, vec = get_median(A.pos, B.pos)
        manager = StraightBlockManager(-1e6, 1e6)

        for P in points:
            if P == A or P == B:
                continue

            # line to line intersection
            if abs(A.weight-P.weight) < smol:

                X = get_equidistant(A.pos, B.pos, P.pos)

                if X is None:
                    # edge case where A, B and P are aligned
                    # intersection point impossible
                    # in this case, either P doesn't affect anything, or it
                    # blocks the entire thing
                    # depending on the ordering of the points

                    if get_dot(v2(P.pos.x-A.pos.x, P.pos.y-A.pos.y),
                               v2(P.pos.x-B.pos.x, P.pos.y-B.pos.y)) < 0:
                        # P is between A and B
                        return False
                    continue

                # get how far down the line this point is
                t = get_t(mid, vec, X)

                # get which bound is being modified by looking at
                # which side of (AB) P is
                H = get_closest_to_line(mid, vec, P.pos)
                t_side = get_t(mid, vec, H)

                if t_side < 0:
                    manager.block_min(t)
                else:
                    manager.block_max(t)

            # line to circle intersection
            else:

                circle = get_circle(A, P)
                intersections = circle_inter_line(mid, vec, circle)

                if not intersections:
                    # circle around P: do nothing
                    if A.weight < P.weight:
                        continue

                    # circle around A: block everything
                    return False

                t0 = get_t(mid, vec, intersections[0])
                t1 = get_t(mid, vec, intersections[1])

                if t0 > t1:
                    t0, t1 = t1, t0

                # circle around P: block the range between the two points
                if A.weight < P.weight:
                    manager.add_block((t0, t1))

                # circle around A: block two ranges outside of the two points
                else:
                    manager.block_min(t0)
                    manager.block_max(t1)

            if manager.is_blocked:
                return False

        return True

    else:
        # make sure the circle is centered around A
        if A.weight < B.weight:
            A, B = B, A

        circle = get_circle(A, B)
        manager = CircleBlockManager()

        for P in points:
            if P == A or P == B:
                continue

            # line to circle intersection
            if abs(A.weight - P.weight) < smol:
                mid, vec = get_median(A.pos, P.pos)
                intersections = circle_inter_line(mid, vec, circle)

                if len(intersections) < 2:
                    continue

                # block a part of the circle

                da = intersections[0]-A.pos
                db = intersections[1]-A.pos
                a_a = atan2(da.y, da.x)
                a_b = atan2(db.y, db.x)

                if a_b < a_a:
                    a_b += tau

                # find which side of the circle is blocked by checking which
                # intersection point, once rotated 90deg, is closest to P

                if get_dist2(circle[0] + v2(-sin(a_a), cos(a_a)), P.pos) < \
                        get_dist2(circle[0] + v2(-sin(a_b), cos(a_b)), P.pos):
                    manager.add_block((a_a, a_b))
                else:
                    manager.add_block((a_b, a_a+tau))

            # circles intersection
            else:
                # todo: cache circle intersections etc at first
                other = get_circle(A, P)
                intersections = circle_inter(circle, other)

                """
                if len(intersections) < 2:
                    if other[1] < circle[1]:
                        if get_dist2(A.pos, P.pos) > circle[1] \
                                and A.weight < P.weight:
                            continue

                        if A.weight < P.weight:
                            continue
                        return False

                    continue
                """
                if len(intersections) < 2:
                    if other[1] < circle[1] and A.weight > P.weight:
                        return False
                    continue

                # compute which side of the circle will be blocked, depending on
                # where P is: find the center of the arc created by the block,
                # and see whether it is closer than the original edge

                da = intersections[0]-circle[0]
                db = intersections[1]-circle[0]
                a_a = atan2(da.y, da.x)
                a_b = atan2(db.y, db.x)

                if a_b < a_a:
                    a_b += tau

                a_mid = (a_a+a_b) / 2
                mid = circle[0] + v2(cos(a_mid), sin(a_mid))*sqrt(circle[1])

                # flip condition if the other circle is centered around A, as
                # that means the incut part of the edgeis the one that is the
                # most outside of the second circle instead of inside
                cond = get_dist2(other[0], mid) < other[1]
                cond ^= A.weight >= P.weight

                manager.add_block((a_a, a_b) if cond else (a_b, a_a+tau))

            if manager.is_blocked:
                return False

        return True

# duplicate from test.py
def get_dist2(point, pos, weight=1):
    dx = (point.x-pos.x) * weight
    dy = (point.y-pos.y) * weight

    return dx*dx + dy*dy


def bad_voronoi(surf, points, step=2):
    # draw cells
    for x in range(0, W, step):
        for y in range(0, H, step):
            min = -1
            mind = 0

            pixel = v2(x+.5, y+.5)
            for i, point in enumerate(points):
                d = get_dist2(point.pos, pixel, point.weight)

                if d < mind or min == -1:
                    min = i
                    mind = d

            pygame.draw.rect(surf, colors[min], Rect(x, y, step, step))


voronoi_surf = pygame.Surface((W, H))
bad_voronoi(voronoi_surf, points)

run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or \
                event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False

        if event.type == MOUSEBUTTONUP:
            bad_voronoi(voronoi_surf, points)

    screen.blit(voronoi_surf, (0, 0))

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

                try:
                    ab = get_circle(points[i], points[j])
                    ac = get_circle(points[i], points[k])
                except ZeroDivisionError:
                    continue

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
