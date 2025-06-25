from classes.v2 import v2

class Cell:
    def __init__(self, pos: v2, weight: float):
        self.pos = pos
        self.weight = weight

    def __repr__(self) -> str:
        return 'Cell<(%d, %d), w=%.3f>' %(*self.pos, self.weight)
