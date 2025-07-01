from utils import smol, perp_bisector, get_equidistant, get_circle, \
        closest_cell, circle_inter, circle_inter_line

from classes.v2 import v2
from classes.cell import Cell, FakeCell
from classes.bounds import Bounds
from classes.intersection import Intersection


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


def add_inter(bounds: Bounds, cells: list[Cell],
              intersections: list[Intersection], inter: v2, component: int,
              i: int, j: int, C: Cell):
    """
    Helper function, used to make several checks to an intersection point
    before adding it to a list
    """

    # check if the intersection point is part of the cell
    if closest_cell(cells, inter) not in (i, j):
        return

    # check if the intersection is inside the bounds
    if component:
        if not bounds.left <= inter.x <= bounds.right:
            return
    else:
        if not bounds.top <= inter.y <= bounds.bottom:
            return

    intersections.append(Intersection(inter, {cells[i], cells[j], C}))


def bounds_intersections(bounds: Bounds, cells: list[Cell]
                         ) -> tuple[list[Intersection], list[FakeCell]]:

    intersections = []

    # create fake cells for the intersection with the bounds
    names = ["top", "right", "bottom", "left"]
    fake_cells = [FakeCell(pos, names[i])
                  for i, pos in zip(range(4), bounds.fake_pos)]

    # cache some shorthand variables that help the code be smaller
    sides = (bounds.top, bounds.right, bounds.bottom, bounds.left)
    components = (1, 0, 1, 0)

    for i, A in enumerate(cells):
        for j, B in enumerate(cells):
            if i == j:
                continue

            if abs(A.weight - B.weight) < smol:
                # find the intersection point of the two cells and the bounds
                line = perp_bisector(A.pos, B.pos)

                for c, target, component in zip(range(4), sides, components):
                    div = line.u[component]
                    if not div:
                        continue

                    t = (target - line.M[component]) / div

                    inter = line.M + line.u*t

                    add_inter(bounds, cells, intersections, inter,
                              component, i, j, fake_cells[c])

            else:
                circle = get_circle(A, B)

                for c, (line, _), component in zip(
                        range(4), bounds.lines, components):

                    for inter in circle_inter_line(line, circle):
                        # check if the intersection point is part of the cell
                        if closest_cell(cells, inter) not in (i, j):
                            continue

                        add_inter(bounds, cells, intersections, inter,
                                  component, i, j, fake_cells[c])

    # add the corner intersections
    for i, corner in enumerate(bounds.corners):
        # find the indices of the neighboring sides
        c0 = fake_cells[i//2 * 2]
        c1 = fake_cells[1 + 2 * (i == 0 or i == 3)]

        intersections.append(Intersection(
            corner, {cells[closest_cell(cells, corner)], c0, c1}))

    # remove duplicate intersections
    final = []
    for inter in intersections:
        if inter not in final:
            final.append(inter)

    return final, fake_cells


def all_intersections(bounds: Bounds, cells: list[Cell],
                      neighbors: list[list[int]]
                      ) -> tuple[list[Intersection], list[FakeCell]]:

    inter1 = cells_intersections(bounds, cells, neighbors)
    inter2, fake_cells = bounds_intersections(bounds, cells)

    return inter1+inter2, fake_cells
