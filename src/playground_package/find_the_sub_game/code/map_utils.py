import numpy as np

from playground_package.find_the_sub_game.code.types import ProbMap


def generate_uniform_map(rows: int, cols: int) -> ProbMap:
    map = np.ones((rows, cols), dtype=float)
    map = map / map.sum()

    return map


def generate_gaussian_blob_map(rows, cols, n_blobs=3, rng=None) -> ProbMap:
    """Random prior: a few Gaussian hotspots on a small flat background."""

    rng = np.random.default_rng(rng)

    # Row number and column number of every square, as two (rows, cols) grids
    # (see PingSensorSpec.detect_grid for a small example).
    r, c = np.indices((rows, cols))
    map_arr = np.full((rows, cols), 0.01)  # small background so no square is impossible
    for _ in range(n_blobs):
        center_r, center_c = rng.uniform(0, rows), rng.uniform(0, cols)
        width = rng.uniform(1, max(rows, cols) / 3)
        height = rng.uniform(0.3, 1)

        # Squared distance from the blob's centre to every square at once:
        # a grid minus a number subtracts it from every cell.
        dist_sq = (r - center_r) ** 2 + (c - center_c) ** 2

        # A bell-shaped bump: `height` at the centre, fading with distance;
        # `width` sets how fast. np.exp works cell by cell on the whole grid.
        map_arr += height * np.exp(-dist_sq / (2 * width**2))

    return map_arr / map_arr.sum()  # normalise: all squares add up to 1


def generate_inverted_map(map_arr: ProbMap) -> ProbMap:
    """The map upside down: likely squares become unlikely and vice versa.

    Flipping within [min, max] keeps every square above 0. A square with
    probability 0 can never come back in a Bayes update, so a plain
    `max - map` would make the original peak impossible to find.
    """
    # Cell by cell: the highest square gets the lowest value and vice versa,
    # e.g. [0.1, 0.3, 0.6] -> 0.7 - [0.1, 0.3, 0.6] = [0.6, 0.4, 0.1].
    flipped = map_arr.max() + map_arr.min() - map_arr
    return flipped / flipped.sum()


def generate_random_map(rows, cols) -> ProbMap:
    rng = np.random.default_rng()
    map = rng.random((rows, cols))
    map = map / map.sum()

    return map



def sample_map_for_sub_location(map: ProbMap) -> tuple[int, int]:
    rng = np.random.default_rng()

    # rng.choice picks from a flat list, so treat the map as one long row:
    # ravel() lays the rows end to end (row 0, then row 1, ...), and the square
    # at flat position i is drawn with probability map.ravel()[i].
    flat_index = rng.choice(map.size, p=map.ravel())

    # Back from "position in the long row" to (row, col):
    # on a 10 x 15 map, flat index 37 is row 37 // 15 = 2, column 37 % 15 = 7.
    sub_location = np.unravel_index(flat_index, map.shape)

    return sub_location