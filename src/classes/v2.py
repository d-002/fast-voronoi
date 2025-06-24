from __future__ import annotations

class v2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, u: v2) -> v2:
        return v2(self.x+u.x, self.y+u.y)

    def __sub__(self, u: v2) -> v2:
        return v2(self.x-u.x, self.y-u.y)

    def __mul__(self, a: float) -> v2:
        return v2(self.x*a, self.y*a)

    def dot(self) -> float:
        return self.x*self.x + self.y*self.y

    def __getitem__(self, i: int) -> float:
        return (self.x, self.y)[i]

    def __repr__(self) -> str:
        return 'v2<%.3f, %.3f>' % (self.x, self.y)
