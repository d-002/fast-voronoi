class Bounds:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x, self.y = x, y
        self.w, self.h = w, h

        self.top = y
        self.right = x+w
        self.bottom = y+h
        self.left = x
