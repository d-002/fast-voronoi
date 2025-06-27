from classes.v2 import v2
from classes.line import Line

class Bounds:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x, self.y = x, y
        self.w, self.h = w, h

        self.top = y
        self.right = x+w
        self.bottom = y+h
        self.left = x

        # set up line objects
        self.lines = [
                (Line(v2(self.left, self.top), v2(1, 0)), v2(0, -1)),
                (Line(v2(self.left, self.top), v2(0, 1)), v2(-1, 0)),
                (Line(v2(self.right, self.top), v2(0, 1)), v2(1, 0)),
                (Line(v2(self.left, self.bottom), v2(1, 0)), v2(0, 1))
        ]

    def is_inside(self, pos: v2) -> bool:
        return self.left <= pos.x <= self.right and \
                self.top <= pos.y <= self.bottom
