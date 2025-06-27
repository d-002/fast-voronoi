from abc import abstractmethod
from math import ceil, tau

from classes.line import Line
from classes.bounds import Bounds


class BlockManager:
    def __init__(self):
        self.blocks: list[tuple[float, float]] = []
        self.is_blocked = False

    @abstractmethod
    def merge_inner(self) -> bool:
        """returns True if merged something, False otherwise"""
        return False

    @abstractmethod
    def check_blocked(self):
        """updates self.is_blocked"""
        pass

    def merge(self):
        while self.merge_inner():
            pass

        self.check_blocked()

    def add_block(self, block):
        self.blocks.append(block)

        self.merge()


class StraightBlockManager(BlockManager):
    def __init__(self, line: Line, box: Bounds):
        super().__init__()

        # init bounds by taking the global bounds into account

        bounds: list[float] = [0]*4

        if line.u.x:
            bounds[0] = (box.left-line.M.x) / line.u.x
            bounds[1] = (box.right-line.M.x) / line.u.x
        if line.u.y:
            bounds[2] = (box.top-line.M.y) / line.u.y
            bounds[3] = (box.bottom-line.M.y) / line.u.y

        if line.u.x:
            if line.u.y:
                bounds.sort()

                self.min = max(bounds[:2])
                self.max = min(bounds[2:])
            else:
                self.min, self.max = sorted(bounds[:2])
        else:
            self.min, self.max = sorted(bounds[2:])

    def merge_inner(self) -> bool:
        for i, block1 in enumerate(self.blocks):
            for j, block2 in enumerate(self.blocks):
                if i == j:
                    continue

                a0, a1 = block1[0], block1[1]
                b0, b1 = block2[0], block2[1]

                # collision
                if a0 <= b1 and a1 >= b0:
                    self.blocks[i] = (min(a0, b0), max(a1, b1))
                    self.blocks.pop(j)
                    return True

        return False

    def check_blocked(self):
        for block in self.blocks:
            if block[0] <= self.min and block[1] >= self.max:
                self.is_blocked = True
                return

        self.is_blocked = False

    def block_min(self, t):
        self.add_block((self.min, t))

    def block_max(self, t):
        self.add_block((t, self.max))


class CircleBlockManager(BlockManager):
    def __init__(self):
        super().__init__()

    def merge_inner(self) -> bool:
        for i, block1 in enumerate(self.blocks):
            for j, block2 in enumerate(self.blocks):
                if i == j:
                    continue

                a0, a1 = block1[0], block1[1]
                b0, b1 = block2[0], block2[1]

                # shift b to be right after a in angle, to avoid modulo issues
                offset = ceil((a0-b0) / tau) * tau
                b0 += offset
                b1 += offset

                # merging occurs
                if a0 <= b0 <= a1:
                    self.blocks[i] = (a0, max(a1, b1))
                    self.blocks.pop(j)

                    return True

        return False

    def check_blocked(self):
        for block in self.blocks:
            if block[1] - block[0] >= tau:
                self.is_blocked = True
                return

        self.is_blocked = False
