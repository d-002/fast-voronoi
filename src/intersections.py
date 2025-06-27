from utils import *

from classes.cell import Cell, FakeCell
from classes.bounds import Bounds
from classes.intersection import Intersection

from utils import closest_cell

def cells_intersections(bounds: Bounds, cells: list[Cell],
                       neighbors: list[list[int]]):
    intersections = []

    for i, A in enumerate(cells):
        for j in neighbors[i]:
            if j < i:
                continue

            B = cells[j]
            ab_is_line = abs(A.weight - B.weight) < smol

            for k in neighbors[j]:
                if k <= i or k < j:
                    continue
                if k not in neighbors[i]:
                    continue

                P = cells[k]

                if ab_is_line:
                    if abs(A.weight - P.weight) < smol:
                        inter = get_equidistant(A.pos, B.pos, P.pos)
                        inters = [] if not inter else [inter]

                    else:
                        line = perp_bisector(A.pos, B.pos)
                        circle = get_circle(A, P)
                        inters = circle_inter_line(line, circle)

                else:
                    if abs(A.weight - P.weight) < smol:
                        line = perp_bisector(A.pos, P.pos)
                        circle = get_circle(A, B)
                        inters = circle_inter_line(line, circle)
                    else:
                        circle1 = get_circle(A, B)
                        circle2 = get_circle(A, P)
                        inters = circle_inter(circle1, circle2)

                if inters is not None:
                    for inter in inters:
                        # check if the intersection is in bounds
                        if not bounds.is_inside(inter):
                            continue

                        # check if the intersection is not blocked
                        if closest_cell(cells, inter) not in (i, j, k):
                            continue

                        intersections.append(Intersection(inter, {A, B, P}))

    return intersections

def bounds_intersections(bounds: Bounds,
                        cells: list[Cell]) -> list[Intersection]:

    intersections = []

    # create fake cells for the intersection with the bounds
    fake_cells = [FakeCell() for _ in range(4)]

    for i, A in enumerate(cells):
        for j, B in enumerate(cells):
            if i == j:
                continue

            if abs(A.weight - B.weight) < smol:
                # find the intersection point of the two cells and the bounds
                line = perp_bisector(A.pos, B.pos)

                sides = (bounds.left, bounds.right, bounds.top, bounds.bottom)
                for c, target, component in zip(range(4), sides, (0, 0, 1, 1)):
                    div = line.u[component]
                    if not div:
                        continue

                    t = (target - line.M[component]) / div

                    inter = line.M + line.u*t

                    # check if the intersection point is part of the cell
                    if closest_cell(cells, inter) not in (i, j):
                        continue

                    # check if the intersection is inside the bounds
                    if component:
                        if not bounds.left <= inter.x <= bounds.right:
                            continue
                    else:
                        if not bounds.top <= inter.y <= bounds.bottom:
                            continue

                    intersections.append(
                            Intersection(inter, {A, B, fake_cells[c]}))

            else:
                pass

    # add the corner intersections
    for i, corner in enumerate(bounds.corners):
        # find the indices of the neighboring sides (left, right, top, btm)
        c0 = fake_cells[i%2]
        c1 = fake_cells[2 + (i//2)]

        intersections.append(Intersection(
            corner, {cells[closest_cell(cells, corner)], c0, c1}))


    return intersections

def all_intersections(bounds: Bounds, cells: list[Cell],
                      neighbors: list[list[int]]) -> list[Intersection]:

    return cells_intersections(bounds, cells, neighbors) + \
            bounds_intersections(bounds, cells)
