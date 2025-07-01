- unify algorithm
- test non weighted, .95
- fix largest cell split into sections that bug
- fix small circles on the side use the wrong radius on the outer part
-  fix larger cell [10 cells 1+5 skip .95] cut in two parts but not recognized
-  when points are aligned, sometimes slight angle imprecisions make it so that the wrong point is picked
- commit

- sort cells by weight before return
- try rendering polygons
- commit

- test low cell counts, test a lot, check behavior of large cell with other cells inside
--> don't draw a sub-polygon with only neighbors of higher weight
  --> update: don't do that, case with the largest cell being among all others. instead, just don't draw the largest cell, instead just return a large polygon with just the bounds if more than 1 polygon
    --> update 2: don't even do that, useless optimisation as this could make for a larger polygon to draw for the gpu, and this behavior can happen inside of smaller cells too, not just the largest one. if want to optimize this, will have to somehow detect these redundant polygons and don't draw them
