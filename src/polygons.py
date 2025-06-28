from math import atan2, tau

from utils import smol, perp_bisector, get_circle

from classes.v2 import v2
from classes.cell import Cell, FakeCell
from classes.bounds import Bounds
from classes.line import Line
from classes.circle import Circle

from neighbors import is_neighbor
from intersections import all_intersections


def make_polygons(bounds: Bounds, cells: list[Cell]) -> list[list[list[v2]]]:
    # cache preliminary variables
    edge_cache: list[list[Line|Circle]] = [[] for _ in range(len(cells))]
    neighbors: list[list[int]] = [[] for _ in range(len(cells))]
    inter_angles: list[dict[int, float]] = [{} for _ in range(len(cells))]

    for i, A in enumerate(cells):
        for j, B in enumerate(cells):
            if i == j:
                continue

            if abs(A.weight - B.weight) < smol:
                edge_cache[i].append(perp_bisector(A.pos, B.pos))
            else:
                edge_cache[i].append(get_circle(A, B))

            if is_neighbor(bounds, cells, i, j):
                neighbors[i].append(j)


    intersections, fake_cells = all_intersections(bounds, cells, neighbors)
    total_length = len(cells)+len(fake_cells)
    all_cells = cells+fake_cells

    # list of intersections from every cell, even the fake ones
    # this is because we might need to iterate over the intersections made
    # around a fake cell as part of drawing a real cell
    cells_inter: list[list[int]] = [[] for _ in range(total_length)]

    # distribute intersections by index, for all the cells
    for i, inter in enumerate(intersections):
        for cell in inter.cells:
            cells_inter[all_cells.index(cell)].append(i)

    # cache intersection angles from the center of their cell
    for i, A in enumerate(cells):
        for inter in cells_inter[i]:
            u = intersections[inter].pos - A.pos
            inter_angles[i][inter] = atan2(u.y, u.x)

    # main algorithm
    polygons: list[list[list[v2]]] = [[] for _ in range(len(cells))]

    for n, A in enumerate(cells):
        to_visit = list(cells_inter[n])

        while to_visit:
            # a cell can be split into multiple parts, hence a list of polygons
            polygon = []

            # find the start intersection index, avoiding cells with a lower
            # weight
            i = min(to_visit, key=lambda j: max(map(lambda cell: cell.weight, intersections[j].cells.difference({A}))))

            # other cell we are currently using the border with
            # make sure to pick the cell that has another intersection point
            # a bit more clockwise than the other
            others = intersections[i].cells.difference({A})
            B = next(iter(others)) # default value to be safe
            min_angle = tau
            for B_ in others:

                # find the other points angles using the cell on the inside
                # of the intersection between the two cells
                if A.weight < B_.weight:
                    m = cells.index(B_)
                    angles = inter_angles[m]
                    angle = min((angles[i]-angles[j]) % tau
                                for j in cells_inter[m]
                                if A in intersections[j].cells and i != j)

                # circle around A: go counterclockwise from the center of A
                else:
                    angles = inter_angles[n]
                    angle = min((angles[j]-angles[i]) % tau
                                for j in cells_inter[n]
                                if B_ in intersections[j].cells and i != j)

                if angle < min_angle:
                    B = B_
                    min_angle = angle

            while True:
                to_visit.remove(i)
                polygon.append(intersections[i].pos)

                # find a neighboring intersection point
                next_i = [j for j in to_visit if B in intersections[j].cells]

                # done with this polygon
                if not next_i:
                    break

                # only two intersection points with this other cell:
                # go to the other one
                if len(next_i) == 1:
                    i = next_i[0]

                # multiple intersection points
                else:
                    # circle around B: go clockwise from the center of B
                    if A.weight < B.weight:
                        angles = inter_angles[cells.index(B)]
                        i = min(next_i,
                                key=lambda j: (angles[i]-angles[j]) % tau)

                    # circle around A: go counterclockwise from the center of A
                    else:
                        angles = inter_angles[n]
                        i = min(next_i,
                                key=lambda j: (angles[j]-angles[i]) % tau)

                # update the other cell
                B = next(iter(intersections[i].cells.difference({A, B})))

            polygons[n].append(polygon)

    return polygons
