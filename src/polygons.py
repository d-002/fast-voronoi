from typing import cast

from math import cos, sin, atan2, tau, sqrt, ceil

from utils import smol, segments_density, dot, get_dist2, perp_bisector, get_circle

from classes.v2 import v2
from classes.cell import Cell, FakeCell
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
        # list of neighbors for every cell
        self.neighbors: list[list[int]]
        # correspondence between intersection points and related cells indices,
        # and polygon points (needed since multiple edges can pass through
        # two given intersection points, depending on which cells are at play)
        # will be filled on demand
        self.edge_cache: dict[tuple[int, int, int, int], list[v2]] = {}
        # line or circle objects between cells
        # (some are duplicated, might improve that in the future)
        self.edge_objects: list[dict[int, Line|Circle]]

        # get neighbor relations, cache edge objects
        self.neighbors = [[] for _ in range(len(cells))]
        self.edge_objects = [{} for _ in range(len(cells))]

        for i, A in enumerate(cells):
            for j, B in enumerate(cells):
                if i == j:
                    continue

                if abs(A.weight - B.weight) < smol:
                    self.edge_objects[i][j] = perp_bisector(A.pos, B.pos)
                else:
                    self.edge_objects[i][j] = get_circle(A, B)

                if is_neighbor(bounds, cells, i, j):
                    self.neighbors[i].append(j)

        # get the intersection points and the fake cells
        self.intersections, fake_cells = \
                all_intersections(bounds, cells, self.neighbors)

        self.cells = cells
        self.all_cells = cells+fake_cells

        # distribute intersections by index, for all the cells
        self.cells_inter = [[] for _ in range(len(self.all_cells))]

        for i, inter in enumerate(self.intersections):
            for cell in inter.cells:
                self.cells_inter[self.all_cells.index(cell)].append(i)

        # cache intersection angles from the center of their cell
        self.inter_angles = [{} for _ in range(len(cells))]

        for i, A in enumerate(cells):
            for inter in self.cells_inter[i]:
                u = self.intersections[inter].pos - A.pos
                self.inter_angles[i][inter] = atan2(u.y, u.x)

    def gen_polygon_edge(self, i: int, j: int, A: Cell, B: Cell) -> list[v2]:
        """
        Generates the data returned by self.get_polygon_edge when missing
        """

        i0, i1 = self.intersections[i], self.intersections[j]

        # special case for borders: simply draw a straight line
        if type(A) == FakeCell or type(B) == FakeCell:
            return [i0.pos, i1.pos]

        # normal cells

        # find out the type of edge
        edge = self.edge_objects[self.cells.index(A)][self.cells.index(B)]

        if type(edge) == Line:
            return [i0.pos, i1.pos]

        if type(edge) == Circle:
            # get angles from the circle center
            d1, d2 = i0.pos-edge.c, i1.pos-edge.c
            a1 = atan2(d1.y, d1.x)
            a2 = atan2(d2.y, d2.x)

            # avoid modulo issues, and take case of the angle inversion
            if A.weight > B.weight:
                if a2 < a1:
                    a2 += tau
            else:
                if a1 < a2:
                    a1 += tau

            radius = sqrt(edge.r2)
            N = ceil(abs(a2-a1) * radius * segments_density)

            points = []
            for k in range(0, N+1):
                a = a1 + (a2-a1)*k/N
                points.append(edge.c + v2(cos(a), sin(a))*radius)

            return points

        return [] # should not happen, but let's please the lsp

    def get_polygon_edge(self, i: int, j: int, A: Cell, B: Cell) -> list[v2]:
        """
        Get the set of points to place between two edges when building a
        polygon out of them, using cached data
        i, j: indices for intersections in self.intersections
        A, B: cells on both sides of the edge (explicitely given to avoid
        issues with bounds, or places where on both intersections the cells are
        the same three)
        """

        m, n = self.all_cells.index(A), self.all_cells.index(B)
        key = (i, j, m, n)
        if key in self.edge_cache:
            # remove the last element of the edge since it will be contained in
            # the next edge
            return self.edge_cache[key][:-1]

        key = (j, i, m, n)
        if key in self.edge_cache:
            # the edge might be cached in a different order, reverse and use it
            points = self.edge_cache[key][::-1]

            self.edge_cache[(i, j, m, n)] = points
            return points[:-1]

        # generate new data when needed
        points = self.gen_polygon_edge(i, j, A, B)
        self.edge_cache[(i, j, m, n)] = points
        return points[:-1]

    def build_polygon(self, intersections: list[int],
                      m: int, around: list[Cell]) -> list[v2]:

        """
        Merges cached polygon edges into a full polygon from:
        - a list of indices of intersections in self.intersections
        - the index of the cell we are building around
        - a list of cells bordering each of the polygon edges
        the list of cells starts with the cells bordering the edge between
        the first and second intersection points in the given list
        """

        # create polygon
        polygon = []
        A = self.cells[m]

        length = len(intersections)
        for n, B in zip(range(length), around):
            i, j = intersections[n], intersections[(n+1) % length]

            polygon += self.get_polygon_edge(i, j, A, B)

        # complete the polygon by going back to the start
        polygon.append(polygon[0])

        return polygon

    def build_circle(self, m: int):
        """
        In case a cell has no intersection points, it is just made of one
        circular edge with its only neighbor. Draws that edge.
        """

        # using all_cells but shouldn't have to, since bounds are guaranteed
        # to add an intersection point unless a cell is outside of them, which
        # already causes other issues
        n = min(self.neighbors[m], key=lambda j: self.all_cells[j].weight)

        circle = cast(Circle, self.edge_objects[m][n])

        radius = sqrt(circle.r2)
        N = ceil(tau * radius * segments_density)

        points = []
        for k in range(0, N+1):
            a = tau*k/N
            points.append(circle.c + v2(cos(a), sin(a))*radius)

        return points


def make_polygons(bounds: Bounds, cells: list[Cell]) -> list[tuple[int, list[v2]]]:
    """
    Returns a list of tuples formed with an integer and a polygon.
    The integers refer to the index of the cell that created the polygon.
    A "polygon" is a list of v2 objects, starting and ending on the same point.

    There may be multiple polygons with the same index, as in a weighted
    diagram a cell might be split in multiple distinct parts.
    Additionally, a cell might be completely inside another cell, and form a
    perfect circle. In this case, there is no way to accomodate for the "hole"
    it makes in the larger cell. To accomodate for that, the returned list is
    ordered so that the polygons for larger cells come first in the list.
    """

    cache = Cache(bounds, cells)
    polygons: list[tuple[int, list[v2]]]
    polygons = []

    for m, A in enumerate(cells):
        # intersection points that still need to be processed
        to_visit = list(cache.cells_inter[m])

        # some cells have no intersection points, draw a circle instead
        if not to_visit:
            polygons.append((m, cache.build_circle(m)))
            continue

        # find the set of concerned neighboring cells, and the
        # intersections they contribute in
        neighbors: dict[Cell, list[int]] = {}
        for i in to_visit:
            for B in cache.intersections[i].cells.difference({A}):
                neighbors.setdefault(B, [])
                neighbors[B].append(i)

        # sort these intersections and split them into small edge sections
        pairs: list[tuple[Cell, tuple[int, int]]] = []

        for B, inter in neighbors.items():
            edge_line = type(B) == FakeCell or \
                    abs(A.weight - B.weight) < smol

            if edge_line:
                # special case for lines: easy to sort, just use the rotated
                # vector from A to cell and order by dot
                u = B.pos - A.pos
                u = v2(-u.y, u.x)
                inter.sort(key=lambda i: dot(cache.intersections[i].pos, u))

            elif A.weight > B.weight:
                # sort anticlockwise when the circle is centered around A
                inter.sort(key=lambda i: cache.inter_angles[m][i])
            else:
                # sort clockwise otherwise
                n = cells.index(B)
                inter.sort(key=lambda i: -cache.inter_angles[n][i])

            # The ordering might be offset by angle modulo stuff, fix it:
            # find the midpoint of each of the currently defined intersection
            # pairs, and if, for at least one of them, the cell outside of the
            # circle is not among the closest to this point (aka this pair does
            # not describe an edge between A and B), swap.
            # Need to check all of the edges as, in case of a swap issue, some
            # of the tested edges might still have a midpoint accessible to
            # the cell on the outside of the circle, giving false negatives.
            if not edge_line:
                n = cells.index(B)
                if A.weight < B.weight:
                    inside, outside = B, A
                else:
                    inside, outside = A, B

                edge = cast(Circle, cache.edge_objects[m][n])

                ok = True
                for i in range(0, len(inter), 2):
                    i1, i2 = inter[i], inter[i+1]

                    d1 = cache.intersections[i1].pos-edge.c
                    d2 = cache.intersections[i2].pos-edge.c
                    a1, a2 = atan2(d1.y, d1.x), atan2(d2.y, d2.x)

                    # the sorting is reversed depending on the weights, use the
                    # correct side of the circle
                    if inside == A:
                        if a2 < a1:
                            a2 += tau
                    else:
                        if a1 < a2:
                            a1 += tau

                    amid = (a1+a2) * .5

                    mid = edge.c + v2(cos(amid), sin(amid)) * sqrt(edge.r2)

                    # Sometimes only two cells appear, but the targeted mid
                    # point is outside the bounds. Need to swap in this case
                    if bounds.is_inside(mid):
                        closest = A # dummy value for lsp
                        closest_dist = -1

                        for cell in cells:
                            if cell == inside:
                                continue

                            dist = get_dist2(cell.pos, mid, cell.weight)
                            if dist < closest_dist or closest_dist == -1:
                                closest_dist = dist
                                closest = cell

                        ok = closest == outside
                    else:
                        ok = False

                    if not ok:
                        break

                if not ok:
                    inter.append(inter.pop(0))

            for i in range(0, len(inter), 2):
                pairs.append((B, (inter[i], inter[i+1])))

        # build small sections of the edge
        pairs: list[tuple[Cell, tuple[int, int]]] = []
        for B, inter in neighbors.items():
            if len(inter) == 2:
                pairs.append((B, (inter[0], inter[1])))
            else:
                for i in range(0, len(inter), 2):
                    pairs.append((B, (inter[i], inter[i+1])))

        while pairs:
            first_cell, (i, j) = pairs.pop()
            # points forming the polygon
            points = [i, j]
            # corresponding neighboring cells used for the edges
            other_cells = [first_cell]

            # Merge all of the sections together, stitching using equal
            # intersection points wherever possible. When no more changes are
            # done, this means a cell is split into multiple polygons.
            # In this case, stop and retry later.
            while pairs:
                changes = False
                a, b = points[0], points[-1]

                for index, (B, (i, j)) in enumerate(pairs):
                    if j == a:
                        points.insert(0, i)
                        other_cells.insert(0, B)
                        changes = True
                    elif i == b:
                        points.append(j)
                        other_cells.append(B)
                        changes = True

                    if changes:
                        pairs.pop(index)
                        break

                if not changes:
                    break

            # add polygon
            polygons.append((m, cache.build_polygon(points, m, other_cells)))

    return sorted(polygons, key=lambda p: cells[p[0]].weight)
