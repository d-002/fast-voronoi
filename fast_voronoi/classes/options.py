class Options:
    def __init__(self, **kwargs):
        """
        Set options in the **kwargs argument. Invalid options lead to errors.
        param segments_density: how many segments to subdivide curved lines
            into, per unit of space, to make them renderable as polygons.
            Should be a number smaller than 1 for efficiency when using
            something like Pygame where the unit of space is a pixel, or a
            number greater than 1 when something like Manim is used.

        param divide_lines: whether to subdivide straight portions of the
            polygons the same way, useful when using this package with Manim.
        """

        self.segments_density = .1
        self.divide_lines = False

        for option, value in kwargs.items():
            match option:
                case 'segments_density':
                    if type(value) not in [int, float]:
                        raise TypeError('segments_density should be int|float')
                    self.segments_density = value

                case 'divide_lines':
                    self.divide_lines = bool(value)

                case _:
                    raise ValueError(
                            f'Options received an unknown keyword argument: {option}')
