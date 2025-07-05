import numpy as np
import matplotlib.pyplot as plt
import pygame

from time import time

import importer
from fast_voronoi.polygons import make_polygons
from fast_voronoi import v2, Cell, Bounds, Options

from bad_voronoi import bad_voronoi
from rand_colors import rand_colors

pygame.init()

n_tests = 10


np.random.seed(6)
def test_naive(W: int, H: int, screen: pygame.Surface, cells: list[Cell],
               colors: list[tuple[int, int, int]], bounds: Bounds,
               options: Options):
    bad_voronoi(W, H, screen, cells, colors, 1)


def test_analytic(W: int, H: int, screen: pygame.Surface, cells: list[Cell],
               colors: list[tuple[int, int, int]], bounds: Bounds,
               options: Options):
    for m, polygon in make_polygons(options, bounds, cells):
        pygame.draw.polygon(screen, colors[m], [list(p) for p in polygon])


def test_func(f, w0: int, h0: int, w1: int, h1: int, size_steps: int,
              n_cells: int, weighted: bool) -> dict[int, float]:
    times = {}

    for n in range(size_steps+1):
        t = n/size_steps
        W, H = round(w0 + (w1-w0)*t), round(h0 + (h1-h0)*t)
        screen = pygame.Surface((W, H))

        bounds = Bounds(0, 0, W, H)
        options = Options()
        cells = [Cell(v2(np.random.randint(0, W), np.random.randint(0, H)),
                      1 if not weighted else np.random.random()*4 + 1)
                 for _ in range(n_cells)]
        colors = rand_colors(len(cells))

        total_time = 0

        for _ in range(n_tests):
            t0 = time()
            f(W, H, screen, cells, colors, bounds, options)
            total_time += time()-t0
        print(f'{n_cells} cells, size {W}x{H}...')

        times[max(W, H)] = total_time/n_tests

    return times


ax = plt.figure().add_subplot(projection='3d')

args = {
        'func': test_analytic,
        'name': 'analytic',
        'weighted': False,
        'col': 'g'
}

plt.title(f'Benchmark for {args['name']} method ({
    'weighted' if args['weighted'] else 'non-weighted'}) (average over {
        n_tests} tests)')

print(f'Running benchmark for {args['name']}...')
for n_cells in range(1, 21):
    w0, h0, w1, h1 = 640, 480, 1920, 1080#3840, 2160
    times = test_func(args['func'], w0, h0, w1, h1, 20, n_cells,
                      args['weighted'])

    for size, t in times.items():
        x = size
        y = n_cells
        z = t
        ax.scatter(x, y, z, color=args['col'])
print('Done.')

ax.legend()
ax.set_xlabel('Screen size (max(W, H))')
ax.set_ylabel('Number of cells')
ax.set_zlabel('Time')

ax.view_init(elev=17, azim=-47, roll=0)

plt.show()
