from math import sqrt
from .classes.v2 import v2
from .classes.line import Line
from .classes.cell import Cell
from .classes.circle import Circle

smol = 1e-9


### Basic math utils


def dot(A: v2, B: v2) -> float:
    """
    returns the dot product between two vectors
    """

    return A.x*B.x + A.y*B.y


def get_dist2(a: v2, b: v2, weight: float = 1) -> float:
    """
    returns the squared, multiplicatively weighted Euclidian distance
    between two points
    """

    dx = (a.x-b.x) * weight
    dy = (a.y-b.y) * weight

    return dx*dx + dy*dy


def closest_cell(cells: list[Cell], pos: v2) -> int:
    """
    returns the index of the closest cell to a point,
    taking their weight into account
    """

    closest = None
    closest_i = -1

    for i, cell in enumerate(cells):
        dist = get_dist2(cell.pos, pos, cell.weight)
        if closest is None or dist < closest:
            closest = dist
            closest_i = i

    return closest_i


def get_closest_to_line(line: Line, P: v2) -> v2:
    """
    returns the closest point to P that is inside the given line
    """

    dap = v2(P.x-line.M.x, P.y-line.M.y)
    t = line.u.x*dap.x + line.u.y*dap.y

    return v2(line.M.x + line.u.x*t, line.M.y + line.u.y*t)


def perp_bisector(A: v2, B: v2) -> Line:
    dx, dy = B.x-A.x, B.y-A.y

    mid = (A+B) * .5

    dist_inv = 1 / sqrt(dx*dx + dy*dy)
    u = v2(dy*dist_inv, -dx*dist_inv)

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


### More intricate math utils


def get_equidistant(A: v2, B: v2, C: v2) -> v2 | None:
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

    # handle when A, B and C are aligned: no equidistant point
    # (except in very rare scenarios that it is easier to ignore)
    if abs(u.x*v.y - u.y*v.x) < smol:
        return None

    # find t, or how far down one line the intersection point is
    # multiple definitions of t exist: either how far down (a), or (b) t is
    # this should help avoid divisions by zero (when dividing by v.x or v.y)
    if abs(v.x) < abs(v.y):
        mv = v.x/v.y

        # another potential division by zero, however that should not happen
        # either, since for div to be 0, u and v have to be colinear,
        # which has already been checked above
        div = u.x - mv*u.y

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

    # cache some useful variables
    xa, ya = A.pos.x, A.pos.y
    xb, yb = B.pos.x, B.pos.y
    wa2, wb2 = A.weight*A.weight, B.weight*B.weight

    # first stage: find a set of polynomials, one for x and one for y,
    # defining the boundary between the two cells

    # x polynomial
    a = wa2 - wb2
    b_x = 2 * (xb*wb2 - xa*wa2)
    c_x = wa2*xa*xa - wb2*xb*xb

    # y polynomial
    b_y = 2 * (yb*wb2 - ya*wa2)
    c_y = wa2*ya*ya - wb2*yb*yb

    # second stage: find the circle equation from these polynomials
    # in the form of
    # [(x-alpha_x)**2 + gamma_x] + [(y-alpha_y)**2 + gamma_y] = 0

    # first part of this equation (the part with x)
    alpha_x = b_x / (2*a)
    gamma_x = c_x/a - alpha_x*alpha_x

    # second part (with y)
    alpha_y = b_y / (2*a)
    gamma_y = c_y/a - alpha_y*alpha_y

    # extract the circle center and squared radius from this circle equation
    pos = v2(-alpha_x, -alpha_y)
    r2 = -gamma_x-gamma_y

    return Circle(pos, r2)


def circle_inter(ca: Circle, cb: Circle) -> list[v2]:
    """
    Computes the list of intersections between two circles
    """

    # warning: the radii are squared
    a1, b1 = ca.c
    r1, r2 = ca.r2, cb.r2
    a2, b2 = cb.c

    # cache a few useful variables
    da, db = a2-a1, b1-b2

    # avoid divisions by zero by computing either x or y first
    # the calculations are nearly the same, only a few variable changes to do
    x_first = abs(da) < abs(db)
    if x_first:
        da, db = -db, -da
        a1, b1 = b1, a1
        a2, b2 = b2, a2

    # cache more useful computations
    a12, b12 = a1*a1, b1*b1
    a22, b22 = a2*a2, b2*b2
    da2 = da*da

    # find one component of the solutions with a quadratic equation
    rest = r1 - r2 + a22 - a12 + b22 - b12
    a = 1 + db*db/da2
    b = db*rest / da2 - 2*a1*db/da - 2*b1
    c = rest*rest / (4*da2) - a1*rest/da + a12 + b12 - r1

    solutions = quadratic(a, b, c)

    # find the full 2D positions of the solutions
    if x_first:
        return [v2(x, (2*db*x + rest) / (2*da)) for x in solutions]
    return [v2((2*db*y + rest) / (2*da), y) for y in solutions]


def circle_inter_line(line: Line, circle: Circle) -> list[v2]:
    """
    Computes the list of intersections between a line and a circle
    """

    # cache a few useful variables
    x0, y0 = line.M
    xu, yu = line.u
    xc, yc = circle.c
    r2 = circle.r2

    # avoid divisions by zero by computing either x or y first
    # the calculations are nearly the same, only a few variable changes to do
    x_first = abs(xu) < abs(yu)
    if x_first:
        x0, y0 = y0, x0
        xu, yu = yu, xu
        xc, yc = yc, xc

    # cache more useful computations
    xu2, yu2 = xu*xu, yu*yu
    y02 = y0*y0
    xc2, yc2 = xc*xc, yc*yc

    # find one component of the solutions with a quadratic equation
    a = 1 + yu2/xu2
    b = (2*y0*yu - 2*yc*yu - 2*x0 * yu2/xu) / xu - 2*xc
    c = y02 + xc2 + yc2 - r2 - 2*yc*y0 + x0*yu/xu * (2*yc - 2*y0 + x0*yu/xu)

    solutions = quadratic(a, b, c)

    # find the full 2D positions of the solutions
    if x_first:
        return [v2(y0 + (y-x0) / xu * yu, y) for y in solutions]
    return [v2(x, y0 + (x-x0) / xu * yu) for x in solutions]
