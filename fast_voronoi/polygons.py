from typing import cast

from math import cos, sin, atan2, tau, sqrt, ceil

from .utils import smol, dot, get_dist2, perp_bisector, \
        get_circle

from .classes.v2 import v2
from .classes.cell import Cell, FakeCell
from .classes.intersection import Intersection
from .classes.bounds import Bounds
from .classes.line import Line
from .classes.circle import Circle
from .classes.options import Options

from .neighbors import is_neighbor
from .intersections import all_intersections


class Cache:
    def __init__(self, options: Options, bounds: Bounds, cells: list[Cell]):
        self.options = options

        # intersections angles as seen from each of their related cells
        self.inter_angles: list[dict[int, float]]
        # list of intersections
        self.intersections: list[Intersection]
        # list of intersections indices from every cell, even the fake ones
        self.cells_inter: list[list[int]]
        # list of neighbors for every cell
        self.neighbors: list[list[int]]
        # Mapping between intersection points and related cells indices, and
        # polygon points (needed since multiple edges can pass through two
        # given intersection points, depending on which cells are at play).
        # Will be filled on demand.
        self.edge_cache: dict[tuple[int, int, int, int], list[v2]] = {}
        # line or circle objects between cells
        # (some are duplicated, might improve that in the future)
        self.edge_objects: list[dict[int, Line | Circle]]

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

    def gen_polygon_edge(self, i: int, j: int, m: int, n: int) -> list[v2]:
        """
        Generates the data returned by self.get_polygon_edge when missing.
        i, j: indices in self.intersections for the two ends of the edge
        m, n: indices in self.cells * self.all_cells
        """

        i0, i1 = self.intersections[i], self.intersections[j]

        A, B = self.cells[m], self.all_cells[n]

        # special case for borders: same as when the cells weights are the same
        if A is FakeCell or type(B) is FakeCell or \
                abs(A.weight - B.weight) < smol:

            if not self.options.divide_lines:
                return [i0.pos, i1.pos]

            diff = i1.pos-i0.pos
            length = diff.length()
            N = ceil(length * self.options.segments_density)

            # can happen for very small edges (although the user should try to
            # avoid them)
            if not N:
                N = 1

            points = []
            for k in range(0, N+1):
                points.append(i0.pos + diff*(k/N))

            return points

        # arc edges: approximate them with many points
        circle = cast(Circle, self.edge_objects[m][n])

        # get angles from the circle center
        d1, d2 = i0.pos-circle.c, i1.pos-circle.c
        a1 = atan2(d1.y, d1.x)
        a2 = atan2(d2.y, d2.x)

        # avoid modulo issues, and take case of the angle inversion
        if A.weight > B.weight:
            if a2 < a1:
                a2 += tau
        else:
            if a1 < a2:
                a1 += tau

        radius = sqrt(circle.r2)
        N = ceil(abs(a2-a1) * radius * self.options.segments_density)
        if not N:
            N = 1

        points = []
        for k in range(0, N+1):
            a = a1 + (a2-a1)*k/N
            points.append(circle.c + v2(cos(a), sin(a))*radius)

        return points

    def get_polygon_edge(self, i: int, j: int, m: int, n: int) -> list[v2]:
        """
        Get the set of points to place between two edges when building a
        polygon out of them, using cached data
        i, j: indices for intersections in self.intersections
        m, n: indices for cells in self.cells * self.all_cells on both sides of
        the edge (given because there could be multiple edges using i and j)
        """

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
        points = self.gen_polygon_edge(i, j, m, n)
        self.edge_cache[(i, j, m, n)] = points
        return points[:-1]

    def build_polygon(self, intersections: list[int], m: int,
                      around: list[int], complete_polygon: bool) -> list[v2]:
        """
        Merges cached polygon edges into a full polygon from:
        - a list of indices of intersections in self.intersections
        - the index of the cell we are building around
        - a list of cells indices in self.all_cells, bordering each of the
        polygon edges
        The list of cells starts with the cells bordering the edge between
        the first and second intersection points in around.
        """

        # create polygon
        polygon = []

        length = len(intersections)
        for index, n in zip(range(length), around):
            i, j = intersections[index], intersections[(index+1) % length]

            polygon += self.get_polygon_edge(i, j, m, n)

        # complete the polygon by going back to the start
        if complete_polygon:
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
        N = ceil(tau * radius * self.options.segments_density)

        if N < 3:
            N = 3

        points = []
        for k in range(0, N+1):
            a = tau*k/N
            points.append(circle.c + v2(cos(a), sin(a))*radius)

        return points


def edge_needs_swap(bounds: Bounds, cache: Cache, m: int, n: int,
                    inter: list[int]) -> bool:
    """
    When creating a list of pairs for polygon building, it can happen that the
    sorting is incorrect due to the modular nature of angle measures.
    This ordering might be off by one, creating incorrect pairs of points.
    For example, if two cells have edges from points A and B, and C and D, it
    could happen that the algorithm thinks they are connected by B and C, and
    D and A instead, causing lots of issues.
    To recognize when this happens, find the midpoint of all the currently
    defined edges and check if these points actually belong to an edge (they
    are close to both cells). If they are not, return True, otherwise False.
    False negatives could happen, so check all the edges instead of just one.
    """

    A, B = cache.cells[m], cache.cells[n]

    if A.weight < B.weight:
        inside, outside = B, A
    else:
        inside, outside = A, B

    edge = cast(Circle, cache.edge_objects[m][n])

    for i in range(0, len(inter), 2):
        i1, i2 = inter[i], inter[i+1]

        d1 = cache.intersections[i1].pos-edge.c
        d2 = cache.intersections[i2].pos-edge.c
        a1, a2 = atan2(d1.y, d1.x), atan2(d2.y, d2.x)

        # the sorting is reversed depending on the weights, use the correct
        # side of the circle
        if inside == A:
            if a2 < a1:
                a2 += tau
        else:
            if a1 < a2:
                a1 += tau

        amid = (a1+a2) * .5

        mid = edge.c + v2(cos(amid), sin(amid)) * sqrt(edge.r2)

        # Sometimes only two cells appear, but the targeted mid point is
        # outside the bounds. Need to swap in this case.
        if not bounds.is_inside(mid):
            return True

        # check if the midpoint is next to the right cells
        closest = A  # dummy value for lsp
        closest_dist = -1

        for cell in cache.cells:
            if cell == inside:
                continue

            dist = get_dist2(cell.pos, mid, cell.weight)
            if dist < closest_dist or closest_dist == -1:
                closest_dist = dist
                closest = cell

        if closest != outside:
            return True

    return False


def build_pairs(bounds: Bounds, cache: Cache, m: int, to_visit: list[int]
                ) -> list[tuple[int, tuple[int, int]]]:
    """
    Creates a list of pairs of intersections that define the edge around a cell
    of index m in cache.cells. Compute and return these pairs of intersections,
    such that they are each composed of two points, with the first one being to
    a predetermined "side" of the other one (namely to the right when looking
    at both of them from the center of the current cell) for easier
    computations later.
    """

    A = cache.cells[m]

    # find the set of concerned neighboring cells, and the
    # intersections they contribute in
    neighbors: dict[int, list[int]] = {}
    for i in to_visit:
        for B in cache.intersections[i].cells.difference({A}):
            n = cache.all_cells.index(B)

            neighbors.setdefault(n, [])
            neighbors[n].append(i)

    # sort these intersections and split them into small edge sections
    pairs = []

    for n, inter in neighbors.items():
        B = cache.all_cells[n]

        edge_line = type(B) is FakeCell or abs(A.weight - B.weight) < smol

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
            inter.sort(key=lambda i: -cache.inter_angles[n][i])

        # fix modulo issues to make sure the points are sorted correctly
        if not edge_line:
            if edge_needs_swap(bounds, cache, m, n, inter):
                inter.append(inter.pop(0))

        for i in range(0, len(inter), 2):
            pairs.append((n, (inter[i], inter[i+1])))

    return pairs


def make_polygons(options: Options, bounds: Bounds, cells: list[Cell]
                  ) -> list[tuple[int, list[v2]]]:
    """
    Returns a list of tuples formed with an integer and a polygon.
    The integers refer to the index of the cell that created the polygon.
    A "polygon" is a list of v2 objects.

    There may be multiple polygons with the same index, as in a weighted
    diagram a cell might be split in multiple distinct parts.
    Additionally, a cell might be completely inside another cell, and form a
    perfect circle. In this case, there is no way to accomodate for the "hole"
    it makes in the larger cell. To accomodate for that, the returned list is
    ordered so that the polygons for larger cells come first in the list.
    """

    if not cells:
        return []

    for cell in cells:
        if not bounds.is_inside(cell.pos):
            raise ValueError(f'Cell {cell} is outside the bounds')

    cache = Cache(options, bounds, cells)
    polygons: list[tuple[int, list[v2]]]
    polygons = []

    for m in range(len(cells)):
        # all the intersection points that need to be processed
        to_visit = list(cache.cells_inter[m])

        # some cells have no intersection points, draw a circle instead
        if not to_visit:
            polygons.append((m, cache.build_circle(m)))
            continue

        pairs = build_pairs(bounds, cache, m, to_visit)

        while pairs:
            first_cell, (i, j) = pairs.pop()
            # indices of intersection points forming the polygon
            points: list[int] = [i, j]
            # corresponding neighboring cells indices used for the edges
            other_cells: list[int] = [first_cell]

            # Merge all of the sections together, stitching using equal
            # intersection points wherever possible. When no more changes are
            # done, this means a cell is split into multiple polygons.
            # In this case, stop and retry later.
            while pairs:
                changes = False
                a, b = points[0], points[-1]

                for index, (n, (i, j)) in enumerate(pairs):
                    if j == a:
                        points.insert(0, i)
                        other_cells.insert(0, n)
                        changes = True
                    elif i == b:
                        points.append(j)
                        other_cells.append(n)
                        changes = True

                    if changes:
                        pairs.pop(index)
                        break

                if not changes:
                    break

            # add polygon
            polygon = cache.build_polygon(points, m, other_cells,
                                          options.complete_polygons)
            if len(polygon) > 2:
                polygons.append((m, polygon))

    return sorted(polygons, key=lambda p: cells[p[0]].weight)
