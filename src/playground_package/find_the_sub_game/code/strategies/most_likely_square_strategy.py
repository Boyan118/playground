import numpy as np

from playground_package.find_the_sub_game.code.strategies.ping_strategy import (
    PingStrategy,
)
from playground_package.find_the_sub_game.code.types import ProbMap


class MostLikelySquareStrategy(PingStrategy):
    def __init__(self):
        self.name = "MostLikelySquareStrategy"

    def choose_location(self, map_arr: ProbMap) -> tuple[int, int]:
        # argmax returns a flat index, as if the map were one long row;
        # unravel_index turns it back into (row, col).
        best_location_to_ping = np.unravel_index(np.argmax(map_arr), map_arr.shape)

        return best_location_to_ping