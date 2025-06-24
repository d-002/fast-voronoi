from math import sqrt
from classes.v2 import v2
from classes.line import Line
from classes.cell import Cell
from classes.circle import Circle

smol = 1e-9


## Basic math utils


def get_dist2(point: v2, pos: v2, weight: float = 1) -> float:
    """
    returns the weighted Euclidian distance between two points, squared
    """

    dx = (point.x-pos.x) * weight
    dy = (point.y-pos.y) * weight

    return dx*dx + dy*dy


def dot(A: v2, B: v2) -> float:
    """
    returns the dot product between two vector
    """

    return A.x*B.x + A.y*B.y


def get_closest_to_line(line: Line, P: v2) -> v2:
    """
    returns the closest point to P that is inside the given line
    """

    M = line.M
    u = line.u

    dap = v2(P.x-M.x, P.y-M.y)
    t = u.x*dap.x + u.y*dap.y
    return v2(M.x + u.x*t, M.y + u.y*t)


def perp_bisector(A: v2, B: v2) -> Line:
    dx, dy = B.x-A.x, B.y-A.y

    mid = (A+B) * .5

    dist = 1 / sqrt(dx*dx + dy*dy)
    u = v2(dy*dist, -dx*dist)

    return Line(mid, u)


def get_t(line: Line, P: v2) -> float:
    """
    returns how far P is along the given line. The "origin" (t = 0) is at M,
    and t = 1 is at M+u.
    """

    if abs(line.u.x) < abs(line.u.y):
        return (P.y-line.M.y) / line.u.y

    return (P.x-line.M.x) / line.u.x


def quadratic(a: float, b: float, c: float) -> list[float]:
    """
    Solves a quadratic equation in IR
    """

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


## More intricate math utils


def get_equidistant(A: v2, B: v2, C: v2) -> v2|None:
    """
    Let (a) be the perpendicular bisector between A and B, (b) the one between
    A and C, and X the point equidistant to A, B and C.

    Returns X, computed as the intersection between (a) and (b).
    Returns None if the two lines are parallel.
    """

    a = perp_bisector(A, B)
    b = perp_bisector(A, C)
    u, v = a.u, b.u
    M, N = a.M, b.M

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


def get_circle(A: Cell, B: Cell) -> Circle:
    """
    Finds the circle defined from the intersection
    of two differently weighted cells
    """

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

    return Circle(pos, r2)


def circle_inter(ca: Circle, cb: Circle) -> list[v2]:
    """
    Computes the list of intersections between two circles
    """

    # warning: the radii are squared
    a1, b1 = ca.c
    r1, r2 = ca.r2, cb.r2
    a2, b2 = cb.c

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


def circle_inter_line(line: Line, circle: Circle) -> list[v2]:
    """
    Computes the list of intersections between a line and a circle
    """

    x0, y0 = line.M
    xu, yu = line.u
    xc, yc = circle.c
    r2 = circle.r2

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
