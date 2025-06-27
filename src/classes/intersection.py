from classes.v2 import v2
from classes.cell import Cell

class Intersection:
    id_counter = 0

    def __init__(self, pos: v2, cells: set[Cell]):
        self.id = Intersection.id_counter
        Intersection.id_counter += 1

        self.pos = pos
        self.cells = cells
