import random
from typing import Protocol

import numpy as np

from playground_package.bulls_and_cows.code.bulls_and_cows_game import BullsAndCowsGame
from playground_package.bulls_and_cows.code.feedback_table import OFFSET, row_entropies


class PlayStrategy(Protocol):

    def generate_guess(self) -> str:
        ...

    def record_turn_feedback(self, bulls:int, cows: int):
        ...


class IterateThroughAllPossibilitiesStrategy(PlayStrategy):
    def __init__(self):
       self.guess_tracker = 999

    def generate_guess(self) -> str:
        self.guess_tracker += 1

        if self.guess_tracker >= 10000:
            raise RuntimeError("The strategy has exhausted all possible guesses")

        return str(self.guess_tracker)

    def record_turn_feedback(self, bulls:int, cows: int):
        pass


class EntropyStrategy(PlayStrategy):
    def __init__(
            self,
            max_entropy_for_first_turn: float,
            first_turn_candidates: list[str],
            feedback_table: np.ndarray):
        self.turns_counter = 1

        self._first_turn_candidates = first_turn_candidates
        self._max_entropy_for_first_turn = max_entropy_for_first_turn
        self.feedback_table = feedback_table

        self._last_guess = None
        self._feedbacks = []
        self.remaining_possibilities = [str(x) for x in range(1000, 10000)]


    def set_guess(self, guess: str):
        self.turns_counter += 1
        self._last_guess = guess


    def generate_top_guesses(self) -> list[tuple[str, float]]:
        if self.turns_counter == 1:
            random.shuffle(self._first_turn_candidates)
            top_guesses = self._first_turn_candidates[0:3]
            return [(g, self._max_entropy_for_first_turn) for g in top_guesses]
        else:
            entropies = EntropyStrategy.calc_entropies(self.feedback_table, self.remaining_possibilities)
            top_guesses = list(zip(self.remaining_possibilities, entropies.tolist()))

            top_guesses.sort(key=lambda x: x[1], reverse=True)

            return top_guesses[0:3]


    def generate_guess(self) -> str:
        guesses = self.generate_top_guesses()
        guess, _ = guesses[0]
        self.set_guess(guess)

        return guess


    def record_turn_feedback(self, bulls:int, cows: int):
        self._feedbacks.append( (bulls, cows) )

        last_feedback = self._feedbacks[-1]
        new_set = self.reduce_set(self.remaining_possibilities, self._last_guess, last_feedback)
        self.remaining_possibilities = new_set


    def calc_game_entropy(self) -> float:
        return np.log2(len(self.remaining_possibilities))


    @staticmethod
    def reduce_set(possibilities: list[str], guess: str, bulls_and_cows: tuple[int, int]) -> list[str]:
        reduced_set = [
            candidate for candidate in possibilities
            if BullsAndCowsGame.detect_bulls_and_cows(str(candidate), guess) == bulls_and_cows
        ]

        return reduced_set


    @staticmethod
    def calc_entropies(feedback_table: np.ndarray, possibilities: list[str]) -> np.ndarray:
        """Entropy of each possibility when used as a guess against all the possibilities."""
        indices = np.array([int(p) for p in possibilities]) - OFFSET
        sub_table = feedback_table[np.ix_(indices, indices)]

        return row_entropies(sub_table)



class BaselineStrategy(PlayStrategy):
    def __init__(self):
        self.turns_counter = 0

        self._last_guess = None
        self._feedbacks = []
        self._remaining_possibilities = [str(x) for x in range(1000, 10000)]


    def generate_guess(self) -> str:
        self.turns_counter += 1
        if self.turns_counter == 1:
            guess = random.choice(["1234", "2345", "3456", "4567", "5678", "6789"])
        else:
            last_feedback = self._feedbacks[-1]

            new_set = self.reduce_set(self._remaining_possibilities, self._last_guess, last_feedback)
            self._remaining_possibilities = new_set

            guess = random.choice(self._remaining_possibilities)

        self._last_guess = guess

        return guess


    def record_turn_feedback(self, bulls:int, cows: int):
        self._feedbacks.append( (bulls, cows) )


    @staticmethod
    def reduce_set(possibilities: list[str], guess: str, bulls_and_cows: tuple[int, int]) -> list[str]:
        reduced_set = [
            candidate for candidate in possibilities
            if BullsAndCowsGame.detect_bulls_and_cows(str(candidate), guess) == bulls_and_cows
        ]

        return reduced_set
