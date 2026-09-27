"""
Precomputed Bulls & Cows feedback for every (guess, secret) pair, using numpy.

Instead of calling `detect_bulls_and_cows` 81 million times in a Python loop,
we describe every number with two small arrays (its digits and its digit
counts) and let numpy compare all pairs at once through broadcasting.
"""

import numpy as np

NUMBERS = np.arange(1000, 10000)
OFFSET = 1000  # table index of a number is `number - OFFSET`

# Feedback is encoded as `bulls * 10 + cows`, so 23 means 2 bulls, 3 cows.
# The largest code is 40 (4 bulls), which fits in a uint8 (0..255).
_MAX_CODE = 40

# Number of guesses (rows) processed per loop iteration; see the note on
# chunking in `build_feedback_table`.
_CHUNK = 500


def build_feedback_table() -> np.ndarray:
    """
    Return a (9000, 9000) uint8 table where `table[g, s]` is the encoded
    feedback for guess `g + OFFSET` against secret `s + OFFSET`.

    Example: feedback for guess 1122 against secret 1234 is 1 bull, 1 cow:
        table[1122 - OFFSET, 1234 - OFFSET] == 11
    """
    # --- Step 1: split every number into its digits -----------------------
    # `number // 10**p % 10` picks out one digit:
    #   p=3: 1234 // 1000 % 10 = 1
    #   p=2: 1234 //  100 % 10 = 2
    #   p=1: 1234 //   10 % 10 = 3
    #   p=0: 1234 //    1 % 10 = 4
    # Each expression works on the whole NUMBERS array at once, and np.stack
    # puts the four results side by side as columns:
    #   digits[1234 - OFFSET] == [1, 2, 3, 4]
    #   digits[1122 - OFFSET] == [1, 1, 2, 2]
    # Shape: (9000, 4).
    digits = np.stack(
        [NUMBERS // 10**p % 10 for p in (3, 2, 1, 0)],
        axis=1,
    ).astype(np.int8)

    # --- Step 2: count how often each digit 0-9 appears in each number -----
    # `(digits == d).sum(axis=1)` counts occurrences of digit d in every row.
    # Doing that for d = 0..9 and stacking gives one row of 10 counts per
    # number:
    #   digit       0  1  2  3  4  5  6  7  8  9
    #   1234  ->  [ 0, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    #   1122  ->  [ 0, 2, 2, 0, 0, 0, 0, 0, 0, 0]
    # Shape: (9000, 10).
    digit_counts = np.stack(
        [(digits == d).sum(axis=1) for d in range(10)],
        axis=1,
    ).astype(np.int8)

    n = len(NUMBERS)
    table = np.empty((n, n), dtype=np.uint8)

    # --- Chunking --------------------------------------------------------
    # Steps 3 and 4 compare every guess with every secret. Doing all 9000
    # guesses at once would create a (9000, 9000, 10) intermediate array,
    # about 810 million values. So we fill the table 500 rows (guesses) at a
    # time: each chunk is a (500, 9000, 10) array, about 45 MB of int8.
    for start in range(0, n, _CHUNK):
        guesses = slice(start, start + _CHUNK)

        # --- Step 3: bulls = same digit in the same position -------------
        # Broadcasting: numpy compares arrays of different shapes by
        # stretching every axis of size 1 to match the other array.
        #   guess_digits:  (chunk,    1, 4)  <- `None` inserts an axis of size 1
        #   secret_digits: (    1, 9000, 4)
        #   result:        (chunk, 9000, 4)
        # So same_position[g, s] holds the 4 position-by-position
        # comparisons of guess g with secret s:
        #   1122 vs 1234 -> [True, False, False, False]
        # Summing over the last axis counts the True values = bulls.
        guess_digits = digits[guesses, None, :]
        secret_digits = digits[None, :, :]
        same_position = guess_digits == secret_digits
        bulls = same_position.sum(axis=2)  # (chunk, 9000)

        # --- Step 4: cows = shared digits minus bulls ----------------------
        # The number of digits the two numbers share, ignoring position, is
        #   sum over d of min(count in guess, count in secret)
        # Example, 1122 vs 1234:
        #   1122 counts  [0, 2, 2, 0, 0, ...]
        #   1234 counts  [0, 1, 1, 1, 1, ...]
        #   minimum      [0, 1, 1, 0, 0, ...]  -> sum = 2 shared digits
        # A bull is also a shared digit, so this total includes the bulls.
        # Subtracting them leaves the cows: 2 shared - 1 bull = 1 cow.
        # The broadcasting is the same as in step 3, now over the 10 digits:
        #   (chunk, 1, 10) vs (1, 9000, 10) -> (chunk, 9000, 10)
        guess_counts = digit_counts[guesses, None, :]
        secret_counts = digit_counts[None, :, :]
        shared = np.minimum(guess_counts, secret_counts).sum(axis=2)  # (chunk, 9000)
        cows = shared - bulls

        table[guesses] = bulls * 10 + cows

    return table


def row_entropies(table: np.ndarray) -> np.ndarray:
    """
    For each row (a guess), the entropy in bits of the feedback distribution
    over the row's columns (the possible secrets).

    Row i of the result is what `calc_entropy` in the notebook computes with a
    Counter: count how often each feedback code occurs, turn the counts into
    probabilities p, and return -sum(p * log2(p)).
    """
    n_rows, n_cols = table.shape
    codes = _MAX_CODE + 1  # possible feedback codes: 0..40
    entropies = np.empty(n_rows)

    for start in range(0, n_rows, _CHUNK):
        chunk = table[start:start + _CHUNK].astype(np.int64)
        rows = len(chunk)

        # --- Count the feedback codes in every row with one bincount -------
        # np.bincount(x)[k] is the number of times value k appears in x. It
        # only works on a flat 1D array, so calling it on the flattened chunk
        # directly would mix the rows together. Instead, shift row i by
        # i * codes so every row gets its own range of bins:
        #   row 0 -> bins    0..40
        #   row 1 -> bins   41..81
        #   row 2 -> bins   82..122  ...
        # Small example with 5 codes instead of 41:
        #   rows      [[0, 1, 1, 4],         shifted  [[0, 1, 1, 4],
        #              [2, 2, 2, 0]]   ->              [7, 7, 7, 5]]   (row 1 + 5)
        #   bincount  [1, 2, 0, 0, 1,  1, 0, 3, 0, 0]
        #   reshape   [[1, 2, 0, 0, 1],   <- row 0: code 0 once, code 1 twice, code 4 once
        #              [1, 0, 3, 0, 0]]   <- row 1: code 0 once, code 2 three times
        # `minlength` makes sure the result has all rows * codes bins even
        # if the highest codes never occur.
        shifted = chunk + codes * np.arange(rows)[:, None]
        counts = np.bincount(shifted.ravel(), minlength=rows * codes)
        counts = counts.reshape(rows, codes)  # counts[i, k]: how often row i has code k

        # --- Entropy per row: -sum(p * log2(p)) -----------------------------
        # Most codes never occur (p = 0). log2(0) is -inf, and 0 * -inf is nan,
        # so we replace those terms with 0 (their limit) and silence the
        # warnings numpy would otherwise print for them.
        p = counts / n_cols
        with np.errstate(divide="ignore", invalid="ignore"):
            terms = np.where(p > 0, p * np.log2(p), 0)
        entropies[start:start + rows] = -terms.sum(axis=1)

    return entropies
