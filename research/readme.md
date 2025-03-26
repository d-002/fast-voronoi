taking rough notes so I don't forget

### Need to create polygons
will use an approximation for the circles.
cannot simply use circles intersection points, since e.g:
- cell A strictly inside cell B doesn't have any intersection points (with a third point = another circle), but there is still a circle edge between A and B
- not precise enough. what to do it not enough points? extrapolate another point? far from the truth, the circle can be off to the side

### What about "holes" in between cells?
making approximations for circles can lead to issues like overlapping or holes.
will use a grid system, with a size that can be set by the user.
snap the points to the nearest grid point to avoid this.
maybe find a correlation between the number of sample points for approximating the circles, and this grid size?
I think we could only ask for a grid size (that can easily be set to the size of a pixel for pixel-perfect graphics), and then compute the number of sample points from the size of an arc

### What about cells in cells?
ordering system.
don't store the inner and outer bounds, too complicated and far from the idea of this project, which is just to get a fast and reliable **rendering** system.
plus, there can be multiple, distinct inner bounds (multiple cells inside one big cell)

### Handling non-convex polygons, "incut" circles from other cells
in the real plane, circles can have at most two intersection points.
to find the polygon:
- cache all angles to all points that are included as neighbors with the intersection points
- find all the intersection points and the data associated with them from the circles (see dedicated section below)
- start at an intersection point
- choose a cell that contributes to this point (cannot be the current cell) and find the other intersection point that includes this cell. as said before, there can only be at most another one:
    * if there is another one: just go to this one
    * if there isn't: we can't exactly use the other cell, as that could cause going backwards. **WILL THEREFORE IGNORE THIS CASE**, since 1. a case where circles exactly touch should never happen and 2. even if it does this is going to be a >3 point intersection, meaning two intersection points will actually get registered (ex ABCD intersection, A touches C in exactly one point, yet there will still be intersection points ABC and ACD)
- choose which cell to go to next: should rotate in a fixed way, say clockwise, for easier computation later. to get the direction, compare the angle to the intersection point with the angles to the related cells. Assuming cells have a weight above zero, the angles should not be zero. Follow along the line made with the other cell that makes a clockwise rotation, meaning (angle_to_point-angle_to_cell) mod 180 < 180.
- two cases here: either this is just drawing an undisturbed part of the circle, or this is an incut circle (or line: compare the weights, see if this is the highest weight among all neighbors - precalculate this, be careful of floating points errors and use an index):
    * drawing circle: draw the line using points (see below), the arc is between this intersection point and the next. be careful about 360deg rotations.
    * incut: draw a series of lines until getting back to the main circle, since there could by multiple incuts merged together. repeat:
        - since we know we are rotating clockwise, we should target the next intersection point accordingly. find the one that is the maximum angle difference (other_angle-current_angle) that is below zero, angles are computed from the intersection point relative to the center of the circle made with the incutting cell. this should give the other end of the arc between the current and other cells.
        - draw the arc
        - if the arc ends in an intersection that includes the current cell as a neighbor, exit this inner loop, since this means we reached the current circle again.
- stop when reaching the same point (index, or compare two related neighbors (?))

add a bunch of points along every added line, which should not include any intersections. in the case of a straight line, add only two points
at the end, remove duplicate points

this has an issue though, since we could start in an inaccessible intersection point (maybe covered by more incuts). to avoid this, we should look for points that include the neighbor with the least weight.

Two things to prove:
1. The neighbor with the highest weight is the one that generates this reference, big circle
we are cutting things out of a circle. the reference circle must be of the highest curvature, and must be a circle centered roughly around/towards the current cell.
therefore the big reference circle must be with the neighbor with the highest weight

2. There will always be such an intersection point
ok, there will not always be one. well that's too bad, but on second thought I guess it doesn't really matter, all that matters is that we stop in the end and don't take the wrong reference circle.
make sure to include a break inside the inner loop

### Finding neighbors
don't just compute all circles and then calculate the intersections between all of them, first this would be like O(n^4) but it just doesn't work
for every cell, find the reference circle (see above), and find all the intersections that include the current cell and the other cell (with regards to the reference circle)
don't need to sort them I think (just putting this in case I said somewhere else that these needed to be sorted)

### Case with less than 3 cells
no intersection points
1 cell: bounds will take care of everything
2 cells: case with no intersection points

Otherwise: will always find either no intersection points, or intersection points with two other cells

### Case with no interseciton points:
just draw a circle

### General algorithm (not handling bounds yet)
- o(n^3) for finding all the circles and intersections of circles between points. use caching. also log which three points are concerned
