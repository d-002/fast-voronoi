from .v2 import v2
from .cell import Cell


class Intersection:
    def __init__(self, pos: v2, cells: set[Cell]):
        self.pos = pos
        self.cells = cells

    def __eq__(self, other):
        return self.pos == other.pos
