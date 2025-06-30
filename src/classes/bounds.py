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

        self.tl = v2(self.left, self.top)
        self.tr = v2(self.right, self.top)
        self.br = v2(self.right, self.bottom)
        self.bl = v2(self.left, self.bottom)

        self.corners = (self.tl, self.tr, self.br, self.bl)

        # set up line objects
        self.lines = [
                (Line(self.tl, v2(1, 0)), v2(0, -1)),
                (Line(self.tr, v2(0, 1)), v2(1, 0)),
                (Line(self.bl, v2(1, 0)), v2(0, 1)),
                (Line(self.tl, v2(0, 1)), v2(-1, 0))
        ]

        # set up positions for when creating fake cells
        # move them out of the box a little to avoid issues
        self.fake_pos = [
            v2(x + w*.5, y - h),
            v2(x + w*2, y + h*.5),
            v2(x + w*.5, y + h*2),
            v2(x - w, y + h*.5)
        ]

    def is_inside(self, pos: v2) -> bool:
        return self.left <= pos.x <= self.right and \
                self.top <= pos.y <= self.bottom
