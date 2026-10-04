import numpy as np

from playground_package.find_the_sub_game.code.strategies.ping_strategy import (
    PingStrategy,
)
from playground_package.find_the_sub_game.code.types import ProbMap


class RandomSquareStrategy(PingStrategy):
    def __init__(self):
        self.name = "RandomSquareStrategy"
        self.counter = 0
        self.all_possibilities = None

    def choose_location(self, map_arr: ProbMap) -> tuple[int, int]:
        if self.all_possibilities is None or self.counter >= len(self.all_possibilities):
            self.counter = 0
            rows, cols = map_arr.shape
            self.all_possibilities = [(r, c) for r in range(rows) for c in range(cols)]
            np.random.shuffle(self.all_possibilities)

        random_location = self.all_possibilities[self.counter]

        self.counter += 1

        return random_location