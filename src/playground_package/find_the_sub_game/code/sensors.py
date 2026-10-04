from enum import Enum

import numpy as np

from playground_package.find_the_sub_game.code.types import ProbMap


class PingResult(Enum):
    DETECTED = 1
    NOT_DETECTED = 0


class PingSensorSpec:
    """What the sensor does, as probabilities: P(Detect) depends only on the
    distance between the pinged square and the sub.

    - distance 0 (the pinged square itself): `p_hit`
    - a neighbor, diagonals included (distance <= sqrt(2)): `p_near`
    - anything further: `p_far`
    """

    def __init__(self, p_hit: float = 0.8, p_near: float = 0.25, p_far: float = 0.001):
        self.p_hit = p_hit
        self.p_near = p_near
        self.p_far = p_far


    def __repr__(self) -> str:
        return f"PingSensorSpec(p_hit={self.p_hit}, p_near={self.p_near}, p_far={self.p_far})"


    def calc_p(
            self,
            of_getting: PingResult,
            at_loc: tuple[int, int],
            given_sub_at: tuple[int, int]) -> float:
        """Probability of a ping outcome, read from the sensor spec.

        Returns P(outcome_A | B): the probability of getting `of_getting` when
        pinging A (`at_loc`), if the sub were at B (`given_sub_at`).

        Examples:
            P(Det_A | B)  probability of a Detect at A, if the sub were at B
            P(ND_A | B)   probability of a No_Detect at A, if the sub were at B

        `given_sub_at` is a supposition. The Bayes update passes every candidate
        square, and `PingSensor.ping` passes the true location.
        """

        dist = self._calculate_distance(at_loc, given_sub_at)
        p_detect_given_distance = float(self._calc_p_detect_given_distance(dist))

        match of_getting:
            case PingResult.DETECTED:
                return p_detect_given_distance
            case PingResult.NOT_DETECTED:
                return 1 - p_detect_given_distance
            case _:
                raise ValueError(f"Unknown outcome: {of_getting}")


    def detect_grid(self, at_loc: tuple[int, int], shape: tuple[int, int]) -> np.ndarray:
        """P(Det at `at_loc` | sub at each square), as a grid of `shape`.

        The same as calling `calc_p(DETECTED, at_loc, square)` for every square,
        without a loop. On a 2 x 3 board pinged at (0, 1):

            [[0.25  0.8   0.25]
             [0.25  0.25  0.25]]
        """
        # np.indices gives two grids of the board's shape holding each square's own
        # row and column number. For a 2 x 3 board:
        #   r = [[0 0 0]      c = [[0 1 2]
        #        [1 1 1]]          [0 1 2]]
        r, c = np.indices(shape)

        # Passing the grids as the "sub location" makes both helpers below work on
        # every square at once: distance grid in, probability grid out.
        return self._calc_p_detect_given_distance(self._calculate_distance(at_loc, (r, c)))


    def _calc_p_detect_given_distance(self, dist: float | np.ndarray) -> float | np.ndarray:
        # np.where(condition, a, b) is an if/else applied to every element:
        # where the condition holds take a, elsewhere take b. Nesting a second
        # np.where in the "else" gives if / elif / else. It works on a single
        # distance (calc_p) and on a whole grid of distances (detect_grid).
        return np.where(dist < 1, self.p_hit,
               np.where(dist <= np.sqrt(2), self.p_near,
                        self.p_far))


    def _calculate_distance(self, pinged_location: tuple[int, int], sub_location: tuple[int, int]):
        # Each location is a (row, col) pair. The parts can be plain numbers, or
        # (for detect_grid) grids of row and column numbers: then `p_x - s_x`
        # subtracts one number from every cell, and the result is a grid of
        # distances, one per square.
        p_x, p_y = pinged_location
        s_x, s_y = sub_location

        return np.sqrt((p_x - s_x) ** 2 + (p_y - s_y) ** 2)


class PingSensor:
    """
    The real sensor: knows where the sub is and simulates pings.
    The detection probabilities come from its `sensor_spec`.
    """

    def __init__(
            self,
            sub_true_location: tuple[int, int],
            map_arr: ProbMap,
            sensor_spec: PingSensorSpec):

        self.rows, self.cols = map_arr.shape
        self.sub_true_location = sub_true_location

        self.sensor_spec = sensor_spec


    def ping(self, pinged_location: tuple[int, int]) -> PingResult:
        x, y = pinged_location
        index_in_range = 0 <= x < self.rows and 0 <= y < self.cols
        if not index_in_range:
            raise ValueError("Coordinates out of bounds")

        p_detect = self.sensor_spec.calc_p(
            of_getting=PingResult.DETECTED, at_loc=pinged_location, given_sub_at=self.sub_true_location)

        return PingResult.DETECTED if np.random.rand() < p_detect else PingResult.NOT_DETECTED