from collections.abc import Callable

from playground_package.find_the_sub_game.code.bayes_game_state import BayesGameState
from playground_package.find_the_sub_game.code.sensors import PingSensor, PingSensorSpec
from playground_package.find_the_sub_game.code.strategies import PingStrategy
from playground_package.find_the_sub_game.code.types import ProbMap


class GameSimulator:
    """Plays one game per sub location in `trials` and records how many pings each took.

    `map` is the belief the strategies start from; `trials` are the true sub
    locations, so a wrong prior is simulated by sampling `trials` from a
    different map.
    """

    def __init__(
            self,
            map: ProbMap,
            trials: list[tuple[int, int]],
            sensor_spec: PingSensorSpec,
            max_turns: int = 1000,
        ):
        self.map = map
        self.trials = trials
        self.sensor_spec = sensor_spec
        self.max_turns = max_turns

    def run(self, strategy_factory: Callable[[PingSensorSpec], PingStrategy]) -> list[int | None]:
        """Pings needed per game; None for a game that hit `max_turns` (lost)."""
        results = []

        for sub_location in self.trials:
            strategy = strategy_factory(self.sensor_spec)
            sensor = PingSensor(sub_true_location=sub_location, map_arr=self.map, sensor_spec=self.sensor_spec)
            game = BayesGameState(
                        sub_location=sub_location,
                        map_array=self.map,
                        sensor=sensor
                    )

            results.append(self._play_game(game, strategy))

        return results


    def _play_game(self, game: BayesGameState, strategy: PingStrategy) -> int | None:
        for turn in range(1, self.max_turns + 1):
            location_to_ping = strategy.choose_location(game.map_array)
            result = game.advance_state(location_to_ping)

            if result.game_won:
                return turn

        return None
