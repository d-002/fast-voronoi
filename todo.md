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
