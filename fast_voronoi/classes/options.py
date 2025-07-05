class Options:
    def __init__(self, segments_density=.1, divide_lines=False):
        """
        param segments_density: how many segments to subdivide curved lines
            into, per unit of space, to make them renderable as polygons.
            Should be a number smaller than 1 for efficiency when using
            something like Pygame where the unit of space is a pixel, or a
            number greater than 1 when something like Manim is used.

        param divide_lines: whether to subdivide straight portions of the
            polygons the same way, useful when using this package with Manim.
        """

        self.segments_density = segments_density
        self.divide_lines = divide_lines
