from classes.v2 import v2


class Line:
    """
    line directed by a vector u and that passes through a given point M
    """

    def __init__(self, M: v2, u: v2):
        self.M = M
        self.u = u
