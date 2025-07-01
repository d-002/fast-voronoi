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
