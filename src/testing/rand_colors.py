from random import randint


def rand_colors(n: int) -> list[tuple[int, int, int]]:
    colors = []

    for _ in range(n):
        colors.append(tuple(randint(127, 255) for _ in range(3)))

    return colors
