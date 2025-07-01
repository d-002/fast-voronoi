# fast-voronoi
Very fast (multiplicatively weighted) Voronoi diagram display.

Requirements:
Should run on Python 3.7+, only tested in Python 3.13.5

## What are Voronoi diagrams?

(from [Wikipedia](https://en.wikipedia.org/wiki/Voronoi_diagram)) A Dirichlet Tesselation, also known as a Voronoi diagram, is a partition of a plane into regions, close to each of a given set of objects.

As such, given a set of sites on a plane, each one has a corresponding Voronoi cell around it, defined by all points in that plane that are closer to it than any other site.

Below is an example of a Voronoi diagram, with the sites as black dots and their cells as colored regions:

![Non-weighted Voronoi diagram](https://github.com/d-002/fast-voronoi/blob/doc/images/non-weighted.png)

There are many ways to define the distance from a point $P=(x,y)$ to a site $S=(x_0,y_0)$, such as the Euclidian distance $(x-x_0)^2+(y-y_0)^2$.
In the case of this distance equation, it is possible for distances to be multiplied by an arbitrary factor. This is called weighted Euclidian distance.

Applying this distance calculation to Voronoi diagrams has many side effects, such as making the boundary between cells curvy, sometimes even splitting them in multiple sections.
Below is the same Voronoi diagram, except with varying weights for the distance calculations with the sites.

![Weighted Voronoi diagram](https://github.com/d-002/fast-voronoi/blob/doc/images/weighted.png)

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
These times are in seconds, an average of 3 runs, executed on my computer with a 12th Gen Intel(R) Core(TM) i7-12700H (20) @ 4.70 GHz.

For the naive approach, the pixels colors are added to a [Pygame Surface](), and for the analytical approach both the polygon creation time and display time (using Pygame polygons rendering) are taken into account for fairness.

These times are in seconds, an average of 3, run on my computer, only here for you to get a rough idea of the performance gain.  
I'm giving 4 non-zero digits no matter the time it takes, so we can easily see which times are smaller.  
The times for the current approach also include any eventual collision removal time, although I think this is too rare to have any impact and is just extra flex.

> [!WARNING]
> These are old benchmark results
> 
> Check the commit at which these were made (before adding POO and weights)  
> I might add a release for this version as it is faster and you may not want the weights feature

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
As you can see, the naive approach takes a lot more time when the screen size increases, while the current approach doesn't care and just increases rapidly when the number of cells increases.
