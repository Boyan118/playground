import random
from enum import Enum


class GameState(Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


class BullsAndCowsGame:
    def __init__(self, external_secret = None):
        self.game_state = GameState.IN_PROGRESS
        self.guess_count = 0

        self.secret = external_secret or str(random.randint(1000, 9999))


    def make_guess(self, guess: str) -> tuple[int, int]:
        if self.game_state != GameState.IN_PROGRESS:
            raise RuntimeError("The game is not in progress")

        BullsAndCowsGame.validate_guess(guess)

        self.guess_count += 1

        bulls, cows = BullsAndCowsGame.detect_bulls_and_cows(self.secret, guess)

        if bulls == 4:
            self.game_state = GameState.WON

        return (bulls, cows)


    @staticmethod
    def validate_guess(guess: str) -> None:
        if not (len(guess) == 4 and guess.isdigit() and guess[0] != "0"):
            raise RuntimeError(f"A guess must be a number from 1000 to 9999, got: {guess!r}")


    @staticmethod
    def detect_bulls_and_cows(secret: str, guess: str) -> tuple[int, int]:
        bulls = 0
        secret_counts = [0] * 10
        guess_counts = [0] * 10

        for s, g in zip(secret, guess):
            if s == g:
                bulls += 1
                continue

            secret_counts[ord(s) - ord('0')] += 1
            guess_counts[ord(g) - ord('0')] += 1

        cows = sum(
            min(s, g)
            for s, g in zip(secret_counts, guess_counts)
        )

        return bulls, cows
