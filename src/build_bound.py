from utils import smol, perp_bisector, get_circle, get_equidistant, circle_inter_line, circle_inter

from classes.cell import Cell
from classes.intersection import Intersection

def find_intersections(cells: list[Cell], neighbors: list[list[int]]):
    intersections = []

    for i, A in enumerate(cells):
        for j in neighbors[i]:
            B = cells[j]
            ab_is_line = abs(A.weight - B.weight) < smol

            for k in neighbors[j]:
                if i == k:
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
                    # need to have the AB circle centered around A
                    A_, B_ = (B, A) if A.weight < B.weight else (A, B)

                    if abs(A_.weight - P.weight) < smol:
                        line = perp_bisector(A_.pos, P.pos)
                        circle = get_circle(A_, B_)
                        inters = circle_inter_line(line, circle)
                    else:
                        circle1 = get_circle(A_, B_)
                        circle2 = get_circle(A_, P)
                        inters = circle_inter(circle1, circle2)

                if inters is not None:
                    for inter in inters:
                        intersections.append(Intersection(inter, A, B, P))

    return intersections
