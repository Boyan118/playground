import numpy as np

from playground_package.find_the_sub_game.code.strategies.ping_strategy import (
    PingStrategy,
)
from playground_package.find_the_sub_game.code.types import ProbMap


class SequentialSquareStrategy(PingStrategy):
    def __init__(self):
        self.name = "SequentialSquareStrategy"
        self.counter = 0

    def choose_location(self, map_arr: ProbMap) -> tuple[int, int]:

        if self.counter >= map_arr.size:
            self.counter = 0

        # The counter walks the flat positions 0, 1, 2, ... (row by row);
        # unravel_index turns each into (row, col).
        next_location = np.unravel_index(self.counter, map_arr.shape)
        self.counter += 1

        return next_location
