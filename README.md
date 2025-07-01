# fast-voronoi
Very fast (multiplicatively weighted) Voronoi diagram display.

Requirements:
Should run on Python 3.7+, only tested in Python 3.13.5.

## What are Voronoi diagrams?

(from [Wikipedia](https://en.wikipedia.org/wiki/Voronoi_diagram)) A Dirichlet Tesselation, also known as a Voronoi diagram, is a partition of a plane into regions, close to each of a given set of objects.

As such, given a set of sites on a plane, each one has a corresponding Voronoi cell around it, defined by all points in that plane that are closer to it than any other site.

Below is an example of a Voronoi diagram, with the sites as black dots and their cells as colored regions:

![Non-weighted Voronoi diagram](https://github.com/d-002/fast-voronoi/blob/main/images/non-weighted.png)

There are many ways to define the distance from a point $P=(x,y)$ to a site $S=(x_0,y_0)$, such as the Euclidian distance $(x-x_0)^2+(y-y_0)^2$.
In the case of this distance equation, it is possible for distances to be multiplied by an arbitrary factor.
This is called weighted Euclidian distance.

Applying this distance calculation to Voronoi diagrams has many side effects, such as making the boundary between cells curvy, sometimes even splitting them in multiple sections.
Below is the same Voronoi diagram, except with varying weights for the distance calculations with the sites.

![Weighted Voronoi diagram](https://github.com/d-002/fast-voronoi/blob/main/images/weighted.png)

## Motivation

Rendering such a diagram on a display surface is very easy: one may iterate over all the pixels, for each of them iterate over all the sites and keep track of which one is the closest.
This will give which site the point is closest to.

This is horrifyingly slow when done iteratively, especially for large pixel counts.
However, the fact that the pixels do not interact with one another can be taken advantage of, by introducing parallel computations, such as by using a [shader](https://en.wikipedia.org/wiki/Shader).
This approach becomes the favorable one, but then the result is confined to the GPU, unless costly operations are executed.

This implementation of Voronoi diagrams aims to take a more analytic approach to this partitioning method, allowing for a fast evaluation of the general shapes of the cells.
It is still possible to render them just like normal, but without the need for an isolated shader.

Thanks to this implementation, methods like [K-means clustering](https://en.wikipedia.org/wiki/K-means_clustering) can be used very easily depending on the context.

This obviously has a few caveats, namely its time complexity - or at least, the one I managed to get - to compute all the relevant information.
For now, the time complexity is around $O(n^3)$.

This might be bad depending on how you intend to use this technique, but for low cell counts and high image resolution it will certainly be worth it.
See [Performance](#user-content-performance).

# Help

I will not give here a complete documentation of the source code, most of the data structures should be easily identifiable by looking at their definition.
If you have any concerns, feel free to open an issue.

Here are some basic points to help with the use of the code:

- `src`: this is the main source directory, containing a subdirectory with testing utilities, another one with utility classes, as well as multiple files:

    - `polygons.py`: this file regroups all the information in the intersections and neighbors scripts (see below), as well as create a list of polygons for every cell in the graph.
    **This is the file to import** if you want to try out this implementation, and the useful function will be `make_polygons()`:  
    This function takes in a `Bounds` object and a list of `Cell` objects, both of which are described below.
    It returns a list of tuple of `(index, polygon)`.
    The index in each one of these tuples is here to identify which cell created the attached polygon, which itself it a list of `v2` objects, which can easily be converted to a more usable format by applying `list()` to them.

    - `intersections.py`: during the process of creating the polygons, it is useful to compute and organize the intersection points between the diagram's cells.
    This file contains utilities to complete these tasks.

    - `neighbors.py`: while creating the polygons, finding out which cells are neighbors of a given cell proves to be useful.
    This file is used in the polygon creation process, but it can be used externally to give further insight on the graph.

    - `test.py`: a Pygame graphical interface used for testing.
    This file shows a lot of debug information about a voronoi graph, and can be used as a kind of tutorial to see how the different useful functions behave.
    It is known to crash, as on very rare occasions (since the points are placed randomly for testing) multiple points may be in the same position, causing divisions by zero or unexpected behavior.

    - `utils.py`: a collection of math utilities used throughout the polygon creation algorithm.
    For example, a way to compute the intersection points between a circle and a line.

> [!WARNING]
> For that reason it is advised to try and avoid this edge case in your applications, either by manually checking for it, or by using techniques that guarantee it will not happen (e.g. hard-coded, distinct sites positions).

- `testing`: this subdirectory contains testing utilities used during the development of this project.
    They are highly turned towards Pygame usage, and help with getting feedback for the project in a graphical way.

- `classes`: this subdirectory contains multiple helper classes, and some of them might be worth knowing about:

    - `Bounds`: cells can span an infinitely large space.
    This does not cause an issue when using the naive approach, as all that is ever rendered is the set of pixels on a surface.
    However, using the analytic approach, it is impossible to know that in advance.
    To address this, it is advised to use the `Bounds` object, that defines the rectangle the polygons will be allowed to exist in.

    - `v2`: a wrapper around two floats, namely to form a position inside a 2D plane.
    Provides additional utilities, like adding such objects, or multiplying them by a number.

    - `Cell`: a site, made of a 2D position (`v2` object) and a weight (floating-point value, should be strictly greater than zero).

## Performance

Below is a comparison between the naive approach (iterate over all the pixels, then check the distance with all the cells) and the analytic approach.
These tests were executed on my computer with a 12th Gen Intel(R) Core(TM) i7-12700H (20) @ 4.70 GHz (and a NVIDIA GeForce RTX 4070 Max-Q / Mobile, although from monitoring its usage I do not think it was actually used that much, even when drawing the polygons on the Surface).

For the naive approach, the pixels colors were added to a [Pygame Surface](https://www.pygame.org/docs/ref/surface.html), and for the analytical approach both the polygon creation time and display time (using Pygame [polygons](https://www.pygame.org/main/ref/draw.html#pygame.draw.polygon) rendering) are taken into account for fairness.

On the left, the naive approach, and on the right, the analytic approach:

- Weighted:

<div align="center">
    <img width="49%" src="https://github.com/d-002/fast-voronoi/blob/main/images/benchmark-naive-weighted.png">
    <img width="49%" src="https://github.com/d-002/fast-voronoi/blob/main/images/benchmark-analytic-weighted.png">
</div>

- Non-weighted (the main difference for the naive approach is that two multiplications are saved):

<div align="center">
    <img width="49%" src="https://github.com/d-002/fast-voronoi/blob/main/images/benchmark-naive-non-weighted.png">
    <img width="49%" src="https://github.com/d-002/fast-voronoi/blob/main/images/benchmark-analytic-non-weighted.png">
</div>

Since the naive approach ran much slower, fewer data points were taken and the results were averaged over less runs.

Still this should not affect results too much, as it is noticeable that **the analytic method is about 240 times faster** than the naive approach for 20 cells, at 2K resolution.

From graph reading is can be seen that the analytic approach processing time increases rapidly when the number of cells increase, namely about on the order of $O(n^3)$.
However it remains almost unaffected by the screen resolution, as all the processing can be dispatched with just a few draw calls to the GPU, one per polygon.

Regarding the naive approach, its time complexity increases linearly with respect to the number of cells, but it also spikes dramatically as the screen size increases.
This correlates with the fact that the time complexity for this method also increases linearly with the number of pixels, that is, quadratically with the display size.

Not to mention that this naive method is already way slower than the analytic approach even for small screen sizes (e.g. in 640x480p, .23s v. .000085s).
Of course, this benchmark is affected greatly by my hardware, the tools inside Pygame, and the fact that this runs on Python, but the results should look the same in other CPU-side implementations.

There are obvious ways to optimize this, this repo was just made as a proof of concept and to explore the math behind Voronoi diagrams.
Some improvements could be to use parallelism, NumPy arrays and vector operations, but I will leave this as an exercise for anyone interested.
