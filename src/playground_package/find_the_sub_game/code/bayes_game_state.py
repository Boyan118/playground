from dataclasses import dataclass

from playground_package.find_the_sub_game.code.sensors import PingResult, PingSensor
from playground_package.find_the_sub_game.code.types import ProbMap


@dataclass(frozen=True)
class GameTurnResult:
    game_won: bool
    pinged_location: tuple[int, int]
    pinged_location_prob: float
    ping_outcome: PingResult


class BayesGameState:
    def __init__(
            self,
            sub_location: tuple[int, int],
            map_array: ProbMap,
            sensor: PingSensor):
        self.sub_location = sub_location
        self.map_array = map_array

        self.sensor = sensor


    def advance_state(self, location_to_ping: tuple[int, int]) -> GameTurnResult:

        location_to_ping_prob = self.map_array[location_to_ping]
        outcome = self.sensor.ping(location_to_ping)

        new_map = self.get_new_belief_map(location_to_ping, outcome)
        self.map_array = new_map

        return GameTurnResult(
            game_won=(location_to_ping == self.sub_location and outcome == PingResult.DETECTED),
            pinged_location=location_to_ping,
            pinged_location_prob = location_to_ping_prob,
            ping_outcome=outcome
        )


    def get_new_belief_map(self, pinged_location: tuple[int, int], outcome: PingResult) -> ProbMap:
        """Bayes' rule for every square at once: P(sub at S | outcome) for all S.

        The four-square example in bayes_search_explained.md, written once for
        the whole grid. Every array below has the map's shape (rows, cols), and
        each operation works cell by cell.
        """
        # P(Det at the pinged square | sub at S), one cell per candidate square S
        p_detect = self.sensor.sensor_spec.detect_grid(pinged_location, self.map_array.shape)

        match outcome:
            case PingResult.DETECTED:
                likelihood = p_detect
            case PingResult.NOT_DETECTED:
                likelihood = 1 - p_detect    # per square: P(ND | S) = 1 - P(Det | S)

        joint = likelihood * self.map_array  # P(outcome | S) · P(S), one cell per square S
        p_outcome = joint.sum()              # P(outcome) = Σ_S P(outcome | S) · P(S)
        return joint / p_outcome             # Bayes: P(S | outcome) = joint / P(outcome)
