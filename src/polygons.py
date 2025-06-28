from math import atan2, tau

from utils import smol, perp_bisector, get_circle

from classes.v2 import v2
from classes.cell import Cell
from classes.intersection import Intersection
from classes.bounds import Bounds
from classes.line import Line
from classes.circle import Circle

from neighbors import is_neighbor
from intersections import all_intersections


class Cache:
    def __init__(self, bounds: Bounds, cells: list[Cell]):
        # intersections angles as seen from each of their related cells
        self.inter_angles: list[dict[int, float]]
        # list of intersections
        self.intersections: list[Intersection]
        # list of intersections indices from every cell, even the fake ones
        self.cells_inter: list[list[int]]

        # correspondence between a pair of intersections and polygon points
        # will be filled on demand
        self.edge_cache: dict[tuple[int, int], list[v2]] = {}
        # line or circle objects between cells
        self.edge_objects: list[list[Line|Circle]]

        # get neighbor relations, cache edge objects
        edges: list[list[Line|Circle]] = [[] for _ in range(len(cells))]
        neighbors: list[list[int]] = [[] for _ in range(len(cells))]

        for i, A in enumerate(cells):
            for j, B in enumerate(cells):
                if i == j:
                    continue

                if abs(A.weight - B.weight) < smol:
                    edges[i].append(perp_bisector(A.pos, B.pos))
                else:
                    edges[i].append(get_circle(A, B))

                if is_neighbor(bounds, cells, i, j):
                    neighbors[i].append(j)

        # get the intersection points and the fake cells
        self.intersections, fake_cells = \
                all_intersections(bounds, cells, neighbors)
        all_cells = cells+fake_cells

        # distribute intersections by index, for all the cells
        self.cells_inter = [[] for _ in range(len(all_cells))]

        for i, inter in enumerate(self.intersections):
            for cell in inter.cells:
                self.cells_inter[all_cells.index(cell)].append(i)

        # cache intersection angles from the center of their cell
        self.inter_angles = [{} for _ in range(len(cells))]

        for i, A in enumerate(cells):
            for inter in self.cells_inter[i]:
                u = self.intersections[inter].pos - A.pos
                self.inter_angles[i][inter] = atan2(u.y, u.x)

    def get_polygon_for_edge(self, i: int, j: int):
        """
        Get the set of points to place between two edges when building a
        polygon out of them, using cached data
        i, j: indices for intersections in self.intersections
        """

        if (i, j) in self.edge_cache:
            return self.edge_cache[(i, j)]

        # the points might be in reverse order
        if (j, i) in self.edge_cache:
            value = self.edge_cache[(j, i)]
            value.reverse()
            self.edge_cache[(i, j)] = value
            return value

        # generate new data
        value = [self.intersections[k].pos for k in (i, j)]
        self.edge_cache[(i, j)] = value
        return value


def find_start(cache: Cache, cells: list[Cell], m: int,
               to_visit: list[int]) -> tuple[int, Cell]:
    """
    Helper function used when creating a polygon. Finds both a start point
    (the index of an intersection point) and a target point (a point that
    will be used to know which way to go when continuing to list the
    polygon points).
    """

    A = cells[m]

    # start the polygon at some intersection point, avoiding points
    # that are part of an intersection with a cell of higher weight,
    # as the algorithm could get stuck
    i = min(to_visit, key=lambda j: max(
            map(lambda cell: cell.weight,
                cache.intersections[j].cells.difference({A}))))

    # find which way to go from this initial intersection
    # we want to rotate in a fixed way (counterclockwise) for later,
    # so choose the point that will help up do that
    others = cache.intersections[i].cells.difference({A})
    B = next(iter(others)) # default value to be safe
    min_angle = tau
    for B_ in others:

        # find the other points angles using the cell on the inside
        # of the intersection between the two cells
        if A.weight < B_.weight:
            n = cells.index(B_)
            angles = cache.inter_angles[n]
            angle = min((angles[i]-angles[j]) % tau
                        for j in cache.cells_inter[n]
                        if A in cache.intersections[j].cells and i != j)

        # circle around A: go counterclockwise from the center of A
        else:
            angles = cache.inter_angles[m]
            angle = min((angles[j]-angles[i]) % tau
                        for j in cache.cells_inter[m]
                        if B_ in cache.intersections[j].cells and i != j)

        if angle < min_angle:
            B = B_
            min_angle = angle

    return i, B


def find_next(cache: Cache, cells: list[Cell], to_visit: list[int],
              i: int, m: int, B: Cell) -> int|None:

    """
    Helper function used when creating a polygon. Chooses a point among a list
    of intersection points indices depending on a few criteria.
    Will be called multiple times, feeding the function's output into itself
    to build a complete polygon.
    Returns the index of the next point if it exists, or None otherwise.
    """

    A = cells[m]

    # find a neighboring intersection point
    next_i = [j for j in to_visit if B in cache.intersections[j].cells]

    # no more available points
    if not next_i:
        return None

    # only two intersection points with this other cell:
    # go to the other one
    if len(next_i) == 1:
        return next_i[0]

    # multiple intersection points

    # the circle is around B: go clockwise from the center of B
    # need to check for B in cells because of cells.index below
    # (B could be a fake cell)
    if B in cells and A.weight < B.weight:
        angles = cache.inter_angles[cells.index(B)]
        return min(next_i,
                   key=lambda j: (angles[i]-angles[j]) % tau)

    # the circle is around A: go counterclockwise from the center of A
    else:
        angles = cache.inter_angles[m]
        return min(next_i,
                   key=lambda j: (angles[j]-angles[i]) % tau)


def make_polygons(bounds: Bounds, cells: list[Cell]) -> list[list[list[v2]]]:
    """
    Returns a list of groups of polygons, one group for every cell passed in
    argument. What is meant by a "group" is that the area controlled by a cell
    can be split in multiple distinct sections, hence why they are in a group.
    A "polygon" is a list of v2 objects, starting and ending on the same point.
    """

    cache = Cache(bounds, cells)
    polygons: list[list[list[v2]]] = [[] for _ in range(len(cells))]

    for m, A in enumerate(cells):
        # intersection points forming the polygon that still remain
        to_visit = list(cache.cells_inter[m])

        while to_visit:
            # a cell can be split into multiple parts, hence a list of polygons
            polygon = []

            i, B = find_start(cache, cells, m, to_visit)

            while True:
                to_visit.remove(i)
                polygon.append(cache.intersections[i].pos)

                i = find_next(cache, cells, to_visit, i, m, B)

                # done with this polygon
                if i is None:
                    break

                # update the other cell
                B = next(iter(cache.intersections[i].cells.difference({A, B})))

            polygons[m].append(polygon)

    return polygons
