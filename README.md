# fast-voronoi
Very fast Voronoi diagram display

## Files defined here

- `voronoi.py` Import this file to access main features
- `test.py` Test file, requires pygame (`pip install pygame`)

## Classes defined here (`voronoi.py`)

- `BoundingBox(l, t, w, h)`
    Similar syntax to [`pygame.Rect`](https://www.pygame.org/docs/ref/rect.html)
    Arguments: `l`: left bound, `t`: top bound, `w`: bound width, `h`: bound height

- `v2(x, y)`
    2D vector

- `Point(x, y, weight=1)`
    `v2`, but with an additional weight argument.
    Represents the center point of a cell.
    Weight: controls the size of the cell around that point. larger values mean bigger cells.

## Important functions defined here (`voronoi.py`)

- `remove_collisions(points)`
    Removes collisions from an array of points.  
    Two points will no longer be able to occupy the same space.  
    I don't really know what happens otherwise, so I made this quick and bad function, ideally you would handle this case yourself and never have to call this unoptimized function.

- `find_neighbors(points, box)`
    Creates and returns an array of `set`s: one set of neighbors per point. The **first** set in the returned array contains all the neighbors for the **first** point in the `points` array, and so on.  
    The `box` parameter is used to only consider cells linked in an enclosed area. This box should be of the defined type `BoundingBox`, but something like a `pygame.Rect` should work too.  
    Here is an example where two cells will definitely be able to join, but outside of the bounding box (the colored portion of the image with cells). In this example, I found it better to not consider the green and brown cells as linked.
<p align=center><img src="https://github.com/user-attachments/assets/fa98b962-9702-4bac-ab2d-940d84e4a410" /></p>

- `make_polygons(points, box)`
    Same parameters as `find_neighbors`. Returns both the result of the latter function, as well as a 2D array of points, as a tuple.  
    The **first** element of the 2D array contains a list of points (correctly ordered) for creating a cell polygon around the **first** point in `points`, and so on.  
    The cells are cropped to make them fit within the bounding box provided.  
    I haven't tested what happens with points outside of the bounding box, but I would suppose something really cool happens or the program just crashes. Sorry for not being even a little more formal but I just needed this for a project and thought this was cool. Do with that what you will.

## Why is this useful?

I have pretty much no formal knowledge on this subject, so I tried to make something relatively efficient, at least on my computer. I will mainly be comparing this approach with the simpler approach of finding which cell each pixel belongs to, which I will call the "naive" approach.

- **Naive approach**
    This approach is very slow on my computer, and that's because I was using only the CPU. It should be pretty fast on a GPU, but I can't be bothered. The complexity is basically $O(N\times n)$, with $N$ being the number of pixels in the image and $n$ being the number of cells. This $N$ value can be very large, and I tried to mitigate this issue with this repo and the following approach.  
    This approach can be tested as well, an implementation has been made in the `test.py` file (`bad_voronoi(points)`).

- **Current approach**
    I tried to treat each cell as one unit, because I wouldn't use that many cells when compared to the possible number of pixels in the image. This way I thought it was a good idea to spend like 8 hours on finding a mathematically slower approach in $O(n^3)$, because here $n$ is significantly smaller than $N$ (if it isn't, either you're doing something wrong, or you should use the naive approach and this repo isn't for you).

## Performance

These times are in seconds, an average of 3, run on my computer, only here for you to get a rough idea of the performance gain.  
I'm giving 4 non-zero digits no matter the time it takes, so we can easily see which times are smaller.  
The times for the current approach also include any eventual collision removal time, although I think this is too rare to have any impact and is just extra flex.

### 1 cell
||32x32|640x480|1280x720|1920x1080|
|-|-|-|-|-|
|Naive approach|0.0006667|0.1420|0.4253|0.9464|
|Current approach|**0**|**0**|**0**|**0** (yes)|

### 10 cells
||32x32|640x480|1280x720|1920x1080|
|-|-|-|-|-|
|Naive approach|**0.0009933**|0.361|1.079|2.405|
|Current approach|0.001002|**0.001672**|**0.001678**|**0.001001**|

### 100 cells
||32x32|640x480|1280x720|1920x1080|
|-|-|-|-|-|
|Naive approach|**0.008667**|2.446|7.343|16.59|
|Current approach|1.4189|**1.5077**|**1.5340**|**1.5137**|

The faster values are **bold** for each test.
As you can see, the naive approach takes a lot more time when the screen size increases, while the current approach doesn't care and just increases rapidly when the number of cells increase.
