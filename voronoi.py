from math import sqrt, atan2, pi, tau

smol = 1e-9

class v2:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def to_tuple(self):
        return (self.x, self.y)

    def __repr__(self):
        return 'v2(%.3f, %.3f)' %(self.x, self.y)

class Point(v2):
    def __init__(self, x, y, weight=1):
        """weight: controls the size of the cell around that point.
        Larger values mean bigger cells."""
        assert weight
        super().__init__(x, y)

        self.weight = weight

def get_dist2(A, B):
    dx = B.x-A.x
    dy = B.y-A.y

    return dx*dx + dy*dy

def get_dot(A, B):
    return A.x*B.x + A.y*B.y

def get_closest_to_line(A, vec, P):
    """return the closest point to P that is inside the line directed by vec
    and that passes through A"""

    dap = v2(P.x-A.x, P.y-A.y)

    t = vec.x*dap.x + vec.y*dap.y

    return v2(A.x + vec.x*t, A.y + vec.y*t)

def get_middle(A, B):
    return Point((A.x+B.x) / 2, (A.y+B.y) / 2)

def get_median(A, B):
    dx, dy = B.x-A.x, B.y-A.y

    mid = get_middle(A, B)
    dab = sqrt(dx*dx + dy*dy)
    u = v2((B.y-A.y) / dab, (A.x-B.x) / dab)

    return mid, u

def get_t(M, u, P):
    if abs(u.x) < abs(u.y):
        return (P.y-M.y) / u.y

    return (P.x-M.x) / u.x

def get_equidistant(A, B, C):
    """
    Let M be the middle point between A and B, and N between A and C
    Let X be the point equidistant to A, B and C.
    X is the intersection between (AB) and (AC)
    return None if the two lines are parallel, X otherwise
    """

    M, u = get_median(A, B)
    N, v = get_median(A, C)

    # handle when A, B and C are aligned
    if abs(u.x*v.y - u.y*v.x) < smol:
        return None

    # handle divisions by zero with multiple definitions of t
    if abs(v.x) < abs(v.y):
        mv = v.x/v.y
        div = u.x - mv*u.y

        # div shouldn't be zero,
        # we checked that above with colinear vectors check
        t = (N.x - M.x + mv * (M.y-N.y)) / div

    else:
        mv = v.y/v.x
        div = u.y - mv*u.x

        t = (N.y - M.y + mv * (M.x-N.x)) / div

    return v2(M.x + u.x*t, M.y + u.y*t)

def find_neighbors(points, box):
    """using this method:
    two cells are neighbors if they share a side. start with a long line (bound
    using the size of the provided boundig box) then, trim this segment by
    computing where, along that line, the points start getting closer to another
    cell (meaning they are inside another cell, and not part of the edge between
          the two current cells
    """

    N = len(points)
    neighbors = [set() for _ in range(N)]

    for i in range(N):
        A = points[i]

        for j in range(N):
            if i == j:
                continue

            B = points[j]

            # get the line equation for points that are equidistant from A and B
            mid, vec = get_median(A, B)

            # define the bounds according to the allowed space
            bounds = [None]*4

            if vec.x:
                # left
                bounds[0] = (box.left-mid.x) / vec.x
                # right
                bounds[1] = (box.right-mid.x) / vec.x

            if vec.y:
                # top
                bounds[2] = (box.top-mid.y) / vec.y
                # bottom
                bounds[3] = (box.bottom-mid.y) / vec.y

            if vec.x:
                if vec.y:
                    bounds.sort()

                    tmin = max(bounds[0], bounds[1])
                    tmax = min(bounds[2], bounds[3])
                else:
                    a, b = bounds[0], bounds[1]
                    if a < b:
                        tmin, tmax = a, b
                    else:
                        tmin, tmax = b, a
            else:
                a, b = bounds[2], bounds[3]
                if a < b:
                    tmin, tmax = a, b
                else:
                    tmin, tmax = b, a

            for k in range(N):
                if k == i or k == j:
                    continue

                P = points[k]

                # find the point H that is at equidistant from A, B and P
                X = get_equidistant(A, B, P)

                if X is None:
                    # edge case where A, B and P are aligned
                    # or the weights and the points distance render an
                    # intersection point impossible
                    # in this case, either P doesn't affect anything, or it
                    # blocks the entire thing
                    # depending on the ordering of the points

                    if get_dot(v2(P.x-A.x, P.y-A.y), v2(P.x-B.x, P.y-B.y)) < 0:
                        # P is between A and B
                        tmin = 1
                        tmax = 0
                        break
                    else:
                        continue

                # get how far down the line this point is
                t = get_t(mid, vec, X)

                # get which bound is being modified by looking at
                # which side of (AB) P is
                H = get_closest_to_line(mid, vec, P)
                t_side = get_t(mid, vec, H)

                if t_side < 0:
                    if t > tmin:
                        tmin = t
                else:
                    if t < tmax:
                        tmax = t

            # there is a point where the i and j cells meet
            if tmin < tmax:
                neighbors[i].add(j)
                neighbors[j].add(i)

    return neighbors

def gradient_move(X, A, B, C):
    """Move a point equidistant from 3 points depending on their weights"""

def insert_in_polygon(polygon, point, angle):
    j = 0
    for j in range(len(polygon)):
        if polygon[j][1] > angle:
            break

    polygon.insert(j, (point, angle))

def complete_polygon(A, B, polygon, points, box):
    """Using this method:
    For each neighbor B, find the ray that originates from the middle point
    between A and B and goes along the neighbor line.
    Then, calculate the intersection points with all four bounds, discarding
    them when they are not part of the current cell.
    Among the remaining ones, the closest intersection to the start of the ray
    is where a point should be added.
    """

    N = len(points)

    mid, vec = get_median(A, B)

    # compute intersections
    inters = []
    mind = None

    for target, index in zip((box.left, box.right, box.top, box.bottom),
                             (0, 0, 1, 1)):
        div = vec.y if index else vec.x
        # no intersection here (vertical/horizontal neighbor line)
        if not div:
            continue

        m = mid.y if index else mid.x
        t = (target-m) / div

        # found the intersection point
        inter = v2(mid.x + vec.x*t, mid.y + vec.y*t)

        # check if this point is actually part of the current cell
        # warning: since the point is on the edge of another cell,
        # need to ignore it as well
        d = get_dist2(A, inter)
        accessible = True
        for k in range(N):
            point = points[k]
            if point == A or point == B:
                continue

            if get_dist2(point, inter) < d:
                accessible = False
                break

        # keep all accessible intersections that don't go out of bounds
        # there may be multiple intersections for lower cell counts
        if accessible:
            if index:
                ok = box.left <= inter.x <= box.right
            else:
                ok = box.top <= inter.y <= box.bottom

            if ok:
                inters.append(inter)

    for inter in inters:
        insert_in_polygon(polygon, inter, atan2(inter.y-A.y, inter.x-A.x))

def make_polygons(points, box):
    polygons = []
    neighbors = find_neighbors(points, box)

    N = len(points)

    sort_n = lambda neighbor: cache[neighbor]
    sort_p = lambda point: point[1]

    # get bound points
    bounds = [
        v2(box.left, box.top),
        v2(box.right, box.top),
        v2(box.left, box.bottom),
        v2(box.right, box.bottom)
    ]

    for i in range(N):
        n = neighbors[i]
        A = points[i]

        # cache angle differences
        cache = {j: atan2(points[j].y-A.y, points[j].x-A.x) for j in n}

        n = sorted(n, key=sort_n)

        # build basic polygon from neighbors intersections
        polygon = [] # list of ((x, y), angle)
        to_fix = [] # list of (point, point)
        for index in range(len(n)):
            j, k = n[index-1], n[index]
            B, C = points[j], points[k]

            # these two neighbors are not linked (probably on the outside of the
            # graph), don't link them
            if k not in neighbors[j]:
                to_fix.append((B, C))

            # no issues, add point to the polygon
            else:
                X = get_equidistant(A, B, C)
                X = gradient_move(X, A, B, C)
                polygon.append((X, atan2(X.y-A.y, X.x-A.x)))

        # fix partially enclosed polygons by adding bound intersections

        # add neighbors separators intersections with bounds if needed
        for B, C in to_fix:
            complete_polygon(A, B, polygon, points, box)
            complete_polygon(A, C, polygon, points, box)

        if not to_fix and len(n) <= 2:
            for j in n:
                complete_polygon(A, points[j], polygon, points, box)

        # add bound points if accessible
        for bound in bounds:
            d = get_dist2(A, bound)
            accessible = True

            for j in range(N):
                if i == j:
                    continue

                if get_dist2(points[j], bound) < d:
                    accessible = False
                    break

            # insert the point at the right index
            if accessible:
                insert_in_polygon(polygon, bound,
                                  atan2(bound.y-A.y, bound.x-A.x))

        # sort the polygon points
        polygon = [point[0] for point in sorted(polygon, key=sort_p)]

        if len(polygon) < 3:
            # veeeeery rare but can happen (basically when like 1000 points
            # align)
            continue

        polygons.append(polygon)

    # might as well return both neighbors graph (undirected) and polygons
    return neighbors, polygons
