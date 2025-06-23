from math import ceil, tau

class BlockManager:
    def __init__(self):
        self.blocks: list[tuple[float, float]] = []

        self.is_blocked = False

    def merge_inner(self):
        """returns True if merged something, False otherwise"""

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
                if a0 < b0 < a1:
                    self.blocks[i] = (a0, max(a1, b1))
                    self.blocks.pop(j)

                    return True

        return False

    def merge(self):
        while self.merge_inner():
            pass

        # check if the circle is entirely covered
        for block in self.blocks:
            if block[1]- block[0] >= tau:
                self.is_blocked = True
                return

        self.is_blocked = False

    def add_block(self, block):
        self.blocks.append(block)

        self.merge()
