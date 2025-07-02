from classes.v2 import v2


class Cell:
    def __init__(self, pos: v2, weight: float = 1):
        self.pos = pos
        self.weight = weight

    def __repr__(self) -> str:
        return 'Cell<(%d, %d), w=%.3f>' % (*self.pos, self.weight)


class FakeCell(Cell):
    """Used for bound points"""

    def __init__(self, pos: v2, name: str):
        super().__init__(pos, 0)
        self.name = name

    def __repr__(self) -> str:
        return f'FakeCell<{self.name}>'
