
from typing import Protocol

from playground_package.find_the_sub_game.code.types import ProbMap


class PingStrategy(Protocol):
    """Protocol — any class with this interface works."""

    def choose_location(self, map_arr: ProbMap) -> tuple[int, int]:
        ...
