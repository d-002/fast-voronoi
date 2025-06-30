from typing import cast

from math import cos, sin, atan2, pi, tau, sqrt, ceil

from utils import smol, segments_density, dot, perp_bisector, get_circle

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
            if a1 < a2:
                a1 += tau

            # fix the angles ordering since we know we go anticlockwise
            # around A and clockwise around B
            if A.weight > B.weight:
                a2 += tau

            radius = sqrt(edge.r2)
            N = ceil(abs(a2-a1) * radius * segments_density)

            points = []
            for k in range(0, N+1):
                a = a1 + (a2-a1)*k/N
                points.append(edge.c + v2(cos(a), sin(a))*radius)

            return points

        return [] # should not happen, but let's please pyright

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
            points = self.edge_cache[key]
            points.reverse()

            self.edge_cache[(i, j, m, n)] = points
            return points[:-1]

        # generate new data when needed
        points = self.gen_polygon_edge(i, j, A, B)
        self.edge_cache[(i, j, m, n)] = points
        return points[:-1]

    def build_polygon(self, intersections: list[int],
                      A: Cell, around: list[Cell]) -> list[v2]:

        """
        Merges cached polygon edges into a full polygon from:
        - a list of indices of intersections in self.intersections
        - the cell we are building around (used in every edge along with: )
        - a list of cells bordering each of the polygon edges
        the list of cells starts with the cells bordering the edge between
        the first and second intersection points in the given list
        """

        # create polygon
        polygon = []

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


def find_start(cache: Cache, cells: list[Cell], m: int,
               to_visit: list[int]) -> tuple[int, Cell]:

    """
    Helper function used when creating a polygon. Finds both a start point
    (the index of an intersection point) and a target point (a point that
    will be used to know which way to go when continuing to list the
    polygon points).
    """

    A = cells[m]

    i = to_visit[0]
    # start the polygon at some intersection point, avoiding points
    # that are part of an intersection with a cell of higher weight,
    # as the algorithm could get stuck
    # warning: using max() with weights of cells that could possibly be fake,
    # but weights should not be negative so that should not be an issue
    i = min(to_visit, key=lambda j: max(
            map(lambda cell: cell.weight,
                cache.intersections[j].cells.difference({A}))))

    """
    # There can be multiple intersection points with
    # these exact other cells B1 and B2, so use the angles to them to find
    # which cell to use as B. This will not work if A has a smaller weight
    # than both B1 and B2, but assuming there are bounds (that induce straight
    # edges, simulating an equal weight) and thanks to the previous i
    # calculation it is guaranteed that this will not happen.
    B1, B2 = cache.intersections[i].cells.difference({A})

    # The target B cell is the one that is on the other side relative to the
    # edge from i to next_i (calculated later). For it to 
    d1, d2 = B1.pos-A.pos, B2.pos-A.pos
    a1, a2 = atan2(d1.y, d1.x), atan2(d2.y, d2.x)
    ai = cache.inter_angles[m][i]
    a1, a2 = (a1-ai) % tau, (a2-ai) % tau

    B = B1 if a1 < a2 else B2
    """

    # Find which way to go from this initial intersection. We want to rotate
    # in a fixed way (anticlockwise) for later, so choose the point B that
    # will help us do that.
    i_pos = cache.intersections[i].pos
    B1, B2 = cache.intersections[i].cells.difference({A})

    # If B1 and B2 are separated by a line, their angular order, compared from
    # the direction or this line, will necessarily match the ordering of their
    # respective cells and will therefore define which cell to pick.
    # An inversion happens depending on which way we are going (towards or away
    # from B1/B2), careful about which way to use for the line direction vector
    if abs(B1.weight - B2.weight) < smol:
        d1, d2 = B1.pos-i_pos, B2.pos-i_pos
        mid = (B1.pos+B2.pos)*.5
        dir = i_pos - mid
        if dot(dir, A.pos-mid) < 0:
            dir *= -1

        a1, a2 = atan2(d1.y, d1.x), atan2(d2.y, d2.x)
        adir = atan2(dir.y, dir.x)
        a1, a2 = (a1-adir) % tau, (a2-adir) % tau

        B = B1 if a1 > a2 else B2

    # If the two other cells are of different weights, get the cell with the
    # larger weight and check whether the center of its circle edge with A (or
    # the point itself if a line edge) is on the correct side for defining the
    # current edge. This can be easily calculated with an angle difference.
    else:
        B = B1 if B1.weight > B2.weight else B2

        if type(B) == FakeCell or abs(A.weight - B.weight) < smol:
            point = B.pos
        else:
            edge = cast(Circle,
                        cache.edge_objects[m][cache.all_cells.index(B)])
            point = edge.c if B.weight > A.weight else A.pos*2 - edge.c

        # getting the angle from A.pos instead of the center of the circle for
        # example, but should not matter as this center, A.pos and point should
        # be aligned
        u = point-A.pos
        ai = cache.inter_angles[m][i]
        if (atan2(u.y, u.x)-ai) % tau > pi:
            B = B2 if B == B1 else B1

    # if the biggest cell out of the three, the logic switches since inside and
    # outside are switched, as well as the target "rotation" direction
    if A.weight < B1.weight and A.weight < B2.weight:
        B = B2 if B == B1 else B1

    """
    # If all three cells have the same weight, there is only one intersection
    # point with all three of them. Pick the cell that is on the left of the
    # intersection point to go to next, as we know we rotate anticlockwise.
    if abs(A.weight - B1.weight) < smol and abs(A.weight - B2.weight) < smol:
        d1, d2 = B1.pos-i_pos, B2.pos-i_pos
        a1, a2 = atan2(d1.y, d1.x), atan2(d2.y, d2.x)
        aa = cache.inter_angles[m][i]+pi
        a1, a2 = (a1-aa) % tau, (a2-aa) % tau

        B = B1 if a1 > a2 else B2

    # If the two other cells that are part of the intersection are of different
    # weight than A, then there can be multiple intersection points with them.
    # Get the other cell with the larger weight and check whether the center
    # of the intersection circle with it (or the cell point itself if a
    # straight line) is on the correct side for defining the current edge.
    # Assuming there are bounds (that induce straight edges) and thanks to the
    # previous i calculation it is guaranteed that A is not of smaller weight
    # than both B1 and B2, which would break the algorithm.
    else:
        B = B1 if B1.weight > B2.weight else B2

        if type(B) == FakeCell or abs(A.weight - B.weight) < smol:
            point = B.pos
        else:
            edge = cast(Circle,
                        cache.edge_objects[m][cache.all_cells.index(B)])
            point = edge.c if B.weight > A.weight else A.pos*2 - edge.c

        # getting the angle from A.pos instead of the center of the circle for
        # example, but should not matter as this center, A.pos and point should
        # be aligned
        u = point-A.pos
        ai = cache.inter_angles[m][i]
        print(B)
        if (atan2(u.y, u.x)-ai) % tau > pi:
            B = B2 if B == B1 else B1
        print(A, B1, B2, B, point, ai, atan2(u.y, u.x)-ai)
    """

    """
    # special case for cells with two intersections points, or more generally
    # when the next point to be visited has the same neighbors: there, both of
    # them will have the same "score", and can't be compared reliably with the
    # algorithm at the end of this function. instead, find the cell that is
    # just to the right of the intersection point (since we are rotating
    # anticlockwise) and use it as a next cell
    alternate_algorithm = False
    if len(to_visit) == 2:
        alternate_algorithm = True
    elif A.weight > max([cells[j].weight for j in cache.neighbors[m]]):
        angles = cache.inter_angles[m]
        next_i = min(to_visit, key=lambda j: (angles[j]-angles[i]) % tau)
        next_others = cache.intersections[next_i].cells.difference({A})
        alternate_algorithm = others == next_others

    ##### TODO: improve this, what about when there is a line intersection?
    ##### the wanted edge might not be to the left
    if alternate_algorithm:
        min_angle = tau
        for B_ in others:
            u = B_.pos-A.pos
            angle = (atan2(u.y, u.x) - cache.inter_angles[m][i]) % tau

            if angle < min_angle:
                min_angle = angle
                B = B_

    # cells with more than two intersection points
    else:
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

            # circle around A: go anticlockwise from the center of A
            else:
                angles = cache.inter_angles[m]
                angle = min((angles[j]-angles[i]) % tau
                            for j in cache.cells_inter[m]
                            if B_ in cache.intersections[j].cells and i != j)

            if angle < min_angle:
                min_angle = angle
                B = B_
    """

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
        return min(next_i, key=lambda j: (angles[i]-angles[j]) % tau)

    # the circle is around A: go anticlockwise from the center of A
    else:
        angles = cache.inter_angles[m]
        return min(next_i, key=lambda j: (angles[j]-angles[i]) % tau)


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
        # intersection points that still need to be processed
        to_visit = list(cache.cells_inter[m])

        # some cells have no intersection points, draw a circle instead
        if not to_visit:
            polygons[m].append(cache.build_circle(m))

        while to_visit:
            # a cell can be split into multiple parts, hence a list of polygons
            polygon = []
            # build a list of the cells that were used to generate the edges
            edges = []

            i, B = find_start(cache, cells, m, to_visit)

            while True:
                to_visit.remove(i)
                polygon.append(i)
                edges.append(B)

                i = find_next(cache, cells, to_visit, i, m, B)

                # done with this polygon
                if i is None:
                    break

                # update the other cell
                B = next(iter(cache.intersections[i].cells.difference({A, B})))

            polygons[m].append(cache.build_polygon(polygon, A, edges))

    return polygons
