import numpy as np

from playground_package.find_the_sub_game.code.sensors import PingSensorSpec
from playground_package.find_the_sub_game.code.strategies.ping_strategy import (
    PingStrategy,
)
from playground_package.find_the_sub_game.code.types import ProbMap


class EntropyBasedStrategy(PingStrategy):
    """Pings the square whose outcome is expected to teach the most about where the sub is."""

    def __init__(self, sensor_spec: PingSensorSpec):
        self.name = "EntropyBasedStrategy"
        self.sensor_spec = sensor_spec
        self._p_table = None


    def choose_location(self, map_arr: ProbMap) -> tuple[int, int]:
        ping_location, _ = self.choose_location_detailed(map_arr)

        return ping_location


    def choose_location_detailed(self, map_arr: ProbMap) -> tuple[tuple[int, int], np.ndarray]:
        """Best location to ping, and the information gain map behind the choice.

        information_gain[r, c] = H(now) - E[H(after pinging (r, c))], in bits.

        For one candidate ping square this is the Bayes update from
        `BayesGameState.get_new_belief_map`, done twice (Detect and No_Detect)
        and then averaged. Here it's done for all candidate squares at once by
        giving every array two extra axes in front: "which square would I ping".

        Shapes, for a board of R rows and C columns:
            (R, C, R, C)  one whole map per candidate ping square
            (R, C)        one number per candidate ping square
        """
        if self._p_table is None:
            self._p_table = self._prepare_calc_p_table(map_arr.shape)

        # --- Joint probabilities: likelihood × prior, for every ping square at once ---
        #
        # self._p_table[pr, pc, sr, sc] = P(Det at (pr, pc) | sub at (sr, sc))   shape (R, C, R, C)
        # map_arr[sr, sc]               = P(sub at (sr, sc))                     shape       (R, C)
        #
        # Broadcasting lines shapes up from the right, so map_arr matches the last
        # two axes (sub_row, sub_col) and is reused for every ping square (pr, pc).
        # Result: joint_detect[pr, pc] is the "likelihood × prior" grid you would
        # get by pinging (pr, pc), the joint column of the four-square example.
        joint_detect = self._p_table * map_arr               # (R, C, R, C)
        joint_non_detect = (1 - self._p_table) * map_arr     # (R, C, R, C), P(ND | sub) = 1 - P(Det | sub)

        # --- P(Det) for every ping square: sum each ping's joint grid ---
        #
        # axis=(2, 3) sums over the sub's row and column, i.e. over "where the sub
        # might be", leaving one number per ping square. P(ND) = 1 - P(Det).
        p_detect = joint_detect.sum(axis=(2, 3))             # (R, C)

        # --- Updated maps: divide each ping's joint grid by that ping's P(outcome) ---
        #
        # p_detect is (R, C) but joint_detect is (R, C, R, C), so the shapes don't
        # line up from the right. [:, :, None, None] adds two axes of length 1:
        # (R, C) -> (R, C, 1, 1). A length-1 axis is stretched to fit, so every
        # cell of ping (pr, pc)'s grid is divided by the same p_detect[pr, pc].
        maps_detect = joint_detect / p_detect[:, :, None, None]                # (R, C, R, C)
        maps_non_detect = joint_non_detect / (1 - p_detect)[:, :, None, None]  # (R, C, R, C)

        # --- Entropy of each updated map: sum over the map's own squares again ---
        detect_entropy = self.calc_entropy(maps_detect, axis=(2, 3))           # (R, C)
        non_detect_entropy = self.calc_entropy(maps_non_detect, axis=(2, 3))   # (R, C)

        # --- Expected entropy after each ping: average over the two outcomes ---
        # E[H(after)] = P(Det) · H(map | Det) + P(ND) · H(map | ND), element by element
        entropy_map = detect_entropy * p_detect + non_detect_entropy * (1 - p_detect)  # (R, C)

        # Back in 2D from here: entropy_map is (rows, cols), current_entropy is one number,
        # and subtracting a number from a grid subtracts it from every cell.
        current_entropy = self.calc_entropy(map_arr)
        information_gain = current_entropy - entropy_map     # (R, C)

        # argmax gives a flat index into the grid (as if it were one long row);
        # unravel_index turns it back into (row, col).
        ping_location = np.unravel_index(np.argmax(information_gain), information_gain.shape)
        return ping_location, information_gain


    def calc_entropy(self, map_arr: np.ndarray, axis: int | tuple[int, ...] | None = None) -> float | np.ndarray:
        """Entropy in bits, H = -Σ p · log2(p).

        axis=None sums over the whole array: one number for a map. With
        axis=(2, 3) on an (R, C, R, C) array, it sums each (R, C) map separately
        and returns one entropy per map.

        The 1e-10 keeps log2 away from log2(0) = -inf. For p = 0 the term is
        0 · log2(1e-10) = 0, which matches the convention 0 · log 0 = 0.
        """
        return np.sum(-map_arr * np.log2(map_arr + 1e-10), axis=axis)


    def _prepare_calc_p_table(self, size: tuple[int, int]) -> np.ndarray:
        """Likelihood table: table[pr, pc] = P(Det at (pr, pc) | sub at each square), a (rows, cols) grid.

        It depends only on the board shape and the sensor spec, never on the map,
        so it's built once and reused every turn.
        """
        at_locations = [(row, col) for row in range(size[0]) for col in range(size[1])]

        p_table_all_locations = np.zeros((size[0], size[1], size[0], size[1]), dtype=float)

        for at_loc in at_locations:
            # Indexing a 4D array with a (row, col) pair selects a whole (rows, cols)
            # grid, the slot for pinging at_loc, and fills it in one go.
            p_table_all_locations[at_loc] = self.sensor_spec.detect_grid(at_loc, size)

        return p_table_all_locations
