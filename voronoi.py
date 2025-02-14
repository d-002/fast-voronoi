from math import sqrt, atan2, pi, tau

smol = 1e-9

class BoundingBox:
    def __init__(self, l, t, w, h):
        self.left = l
        self.right = l+w
        self.top = t
        self.bottom = t+h

def remove_collisions(points):
    """ugly, but needed in case some points are in the same place"""

    N = len(points)
    while True:
        ok = True

        for i in range(N):
            for j in range(N):
                if i == j:
                    continue

                if points[i] == points[j]:
                    points[j] = (points[j][0]+1e-3, points[j][1])
                    ok = False

        if ok:
            return

def get_dist2(A, B):
    dx = B[0]-A[0]
    dy = B[1]-A[1]

    return dx*dx + dy*dy

def get_dot(A, B):
    return A[0]*B[0] + A[1]*B[1]

def get_closest_to_line(A, B, P, only_segment):
    xa, ya = A
    xb, yb = B
    xp, yp = P

    dab = (xb-xa, yb-ya)
    dap = (xp-xa, yp-ya)

    t = (dab[0]*dap[0] + dab[1]*dap[1]) / (dab[0]*dab[0] + dab[1]*dab[1])
    if (t < 0 or t > 1) and only_segment: return

    return (xa + dab[0]*t, ya + dab[1]*t)

def get_middle(A, B):
    return ((A[0]+B[0]) / 2, (A[1]+B[1]) / 2)

def get_median(A, B):
    dx, dy = B[0]-A[0], B[1]-A[1]

    mid = get_middle(A, B)
    dab = sqrt(dx*dx + dy*dy)
    u = ((B[1]-A[1]) / dab, (A[0]-B[0]) / dab)

    return mid, u

def get_t(M, u, P):
    i = 1 if abs(u[0]) < abs(u[1]) else 0

    return (P[i]-M[i]) / u[i]

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
    if abs(u[0]*v[1] - u[1]*v[0]) < smol:
        return None

    # handle divisions by zero with multiple definitions of t
    i0 = 0 if abs(v[0]) < abs(v[1]) else 1
    i1 = 1-i0
    mv = v[i0]/v[i1]
    div = u[i0] - mv*u[i1]

    # div shouldn't be zero, we checked that above with colinear vectors check
    t = (N[i0] - M[i0] + mv * (M[i1]-N[i1])) / div

    return (M[0] + u[0]*t, M[1] + u[1]*t)

def find_neighbors(points, box):
    """using this method:
    two cells are neighbors if they share a side.
    meaning there has to be at least one point that is equally close to them, the two being the closest cells to this point
    obviously there will be floating-point errors, meaning a threshold will have to be used
    or not? build a segment of the line where no other cells are closer
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

            if vec[0]:
                # left
                bounds[0] = (box.left-mid[0]) / vec[0]
                # right
                bounds[1] = (box.right-mid[0]) / vec[0]

            if vec[1]:
                # top
                bounds[2] = (box.top-mid[1]) / vec[1]
                # bottom
                bounds[3] = (box.bottom-mid[1]) / vec[1]

            if vec[0]:
                if vec[1]:
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
                    # in this case, either P doesn't affect anything, or it blocks the entire thing
                    # depending on the ordering of the points

                    if get_dot((P[0]-A[0], P[1]-A[1]), (P[0]-B[0], P[1]-B[1])) < 0:
                        # P is between A and B
                        tmin = 1
                        tmax = 0
                        break
                    else:
                        continue

                # get how far down the line this point is
                t = get_t(mid, vec, X)

                # get which bound is being modified by looking at which side of (AB) P is
                H = get_closest_to_line(mid, (mid[0]+vec[0], mid[1]+vec[1]), P, False)
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

def insert_in_polygon(polygon, point, angle):
    j = 0
    for j in range(len(polygon)):
        if polygon[j][1] > angle:
            break

    polygon.insert(j, (point, angle))

def complete_polygon(A, B, polygon, points, box):
    """using this method:
    for each neighbor B, find the ray that originates from the middle point between A and B and goes along the neighbor line.
    then, calculate the intersection points with all four bounds,
    discarding them when they are not part of the current cell.
    among the remaining ones, the closest intersection to the start of the ray is where a point should be added
    """

    N = len(points)

    mid, vec = get_median(A, B)

    # compute intersections
    closest = None
    mind = None

    for target, index in zip((box.left, box.right, box.top, box.bottom), (0, 0, 1, 1)):
        div = vec[index]
        # no intersection here (vertical/horizontal neighbor line)
        if not div:
            continue

        t = (target-mid[index]) / div

        # found the intersection point
        inter = (mid[0] + vec[0]*t, mid[1] + vec[1]*t)

        # check if this point is actually part of the current cell
        # warning: since the point is on the edge of another cell, need to ignore it as well
        d = get_dist2(A, inter)
        accessible = True
        for k in range(N):
            point = points[k]
            if point == A or point == B:
                continue

            if get_dist2(point, inter) < d:
                accessible = False
                break

        # keep only the closest point amongst those accessible
        if accessible:
            d = get_dist2(mid, inter)

            if mind is None or d < mind:
                mind = d
                closest = inter

    if closest is None:
        return

    insert_in_polygon(polygon, closest, atan2(closest[1]-A[1], closest[0]-A[0]))

def make_polygons(points, box):
    polygons = []
    neighbors = find_neighbors(points, box)

    N = len(points)

    sort_n = lambda neighbor: cache[neighbor]
    sort_p = lambda point: point[1]

    # get bound points
    bounds = [
        (box.left, box.top),
        (box.right, box.top),
        (box.left, box.bottom),
        (box.right, box.bottom)
    ]

    for i in range(N):
        n = neighbors[i]
        x, y = A = points[i]

        # cache angle differences
        cache = {j: atan2(points[j][1]-y, points[j][0]-x) for j in n}

        n = sorted(n, key=sort_n)

        # build basic polygon from neighbors intersections
        polygon = [] # list of ((x, y), angle)
        to_fix = [] # list of (point, point)
        for index in range(len(n)):
            j, k = n[index-1], n[index]
            B, C = points[j], points[k]

            # these two neighbors are not linked (probably on the outside of the graph), don't link them
            if k not in neighbors[j]:
                to_fix.append((B, C))

            # no issues, add point to the polygon
            else:
                X = get_equidistant(A, B, C)
                polygon.append((X, atan2(X[1]-y, X[0]-x)))

        # fix partially enclosed polygons by adding bound intersections

        # add neighbors separators intersections with bounds if needed
        for B, C in to_fix:
            complete_polygon(A, B, polygon, points, box)
            complete_polygon(A, C, polygon, points, box)

        if not to_fix and len(n) <= 2:
            for j in n:
                complete_polygon(A, points[j], polygon, points, box)

        # add bound points if accessible
        for b_index, bound in enumerate(bounds):
            b_index = -1-b_index
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
                insert_in_polygon(polygon, bound, atan2(bound[1]-y, bound[0]-x))

        # sort the polygon points
        polygon = [point[0] for point in sorted(polygon, key=sort_p)]

        polygons.append(polygon)

    # might as well return both neighbors graph (undirected) and polygons
    return neighbors, polygons
