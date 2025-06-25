from utils import smol, perp_bisector, get_circle, get_equidistant, circle_inter_line, circle_inter

from classes.cell import Cell
from classes.intersection import Intersection

from utils import closest_cell

def find_intersections(cells: list[Cell], neighbors: list[list[int]]):
    intersections = []

    for i, A in enumerate(cells):
        for j in neighbors[i]:
            if j < i:
                continue

            B = cells[j]
            ab_is_line = abs(A.weight - B.weight) < smol

            for k in neighbors[j]:
                if k <= i:
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
                        # check if the intersection is not blocked
                        if closest_cell(cells, inter) not in (i, j, k):
                            continue

                        intersections.append(Intersection(inter, A, B, P))

    return intersections
