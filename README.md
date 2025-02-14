# fast-voronoi
Very fast Voronoi diagram display

## Files defined here

- `voronoi.py` Import this file to access main features
- `test.py` Test file, requires pygame (`pip install pygame`)

## Important functions defined here (`voronoi.py`)

- `remove_collisions(points)`
    Removes collisions from an array of points.  
    Two points will no longer be able to occupy the same space.  
    I don't really know what happens otherwise, so I made this quick and bad function, ideally you would handle this case yourself and never have to call this unoptimized function.

- `find_neighbors(points, box)`
    Creates and returns an array of `set`s: one set of neighbors per point. The **first** set in the returned array contains all the neighbors for the **first** point in the `points` array, and so on.  
    The `box` parameter is used to only consider cells linked in an enclosed area. This box should be of the defined type `BoundingBox`, but something like a `pygame.Rect` should work too.  
    Here is an example where two cells will definitely be able to join, but outside of the bounding box (the colored portion of the image with cells). In this example, I found it better to not consider the green and brown cells as linked.

- `make_polygons(points, box)`
    Same parameters as `find_neighbors`. Returns both the result of the latter function, as well as a 2D array of points, as a tuple.  
    The **first** element of the 2D array contains a list of points (correctly ordered) for creating a cell polygon around the **first** point in `points`, and so on.  
    The cells are cropped to make them fit within the bounding box provided.  
    I haven't tested what happens with points outside of the bounding box, but I would suppose something really cool happens or the program just crashes. Sorry for not being even a little more formal but I just needed this for a project and thought this was cool. Do with that what you will.

## Why is this useful?

I have pretty much no formal knowledge on this subject, so I tried to make something relatively efficient, at least on my computer. I will mainly be comparing this approach with the simpler approach of finding which cell each pixel belongs to, which I will call the "naive" approach.

- **Naive approach**
    This approach is very slow on my computer, and that's because I was using only the CPU. It should be pretty fast on a GPU, but I can't be bothered. The complexity is basically $O(N*n)$, with $N$ being the number of pixels in the image and $n$ being the number of cells. This $N$ value can be very large, and I tried to mitigate this issue with this repo and the following approach.

- **Current approach**
    I tried to treat each cell as one unit, because I wouldn't use that many cells when compared to the possible number of pixels in the image. This way I thought it was a good idea to spend like 8 hours on finding a mathematically slower approach in $O(n^3)$, because here $n$ is significantly smaller than $N$ (if it isn't, either you're doing something wrong, or you should use the naive approach and this repo isn't for you).

## Performance
