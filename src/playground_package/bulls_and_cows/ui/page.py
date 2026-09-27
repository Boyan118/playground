import pandas as pd
import streamlit as st

from playground_package.bulls_and_cows.code.bulls_and_cows_game import (
    BullsAndCowsGame,
    GameState,
)
from playground_package.bulls_and_cows.code.feedback_table import FeedbackTable
from playground_package.bulls_and_cows.code.strategies import EntropyStrategy

st.set_page_config(
    page_title="Bulls & Cows",
    page_icon="🐂",
    layout="centered",
)


# ---------------------------------------------------------------------------
# Solver data
# ---------------------------------------------------------------------------

@st.cache_resource
def load_feedback_table() -> FeedbackTable:
    return FeedbackTable()


feedback_table = load_feedback_table()


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------

def new_game():
    st.session_state.game = BullsAndCowsGame()
    st.session_state.strategy = EntropyStrategy(feedback_table)
    st.session_state.history = []
    st.session_state.suggestions = None
    st.session_state.celebrate = False


if "game" not in st.session_state:
    new_game()

# session_state values are untyped; annotate them to get type checking and
# autocompletion back.
game: BullsAndCowsGame = st.session_state.game
strategy: EntropyStrategy = st.session_state.strategy
history: list[dict] = st.session_state.history


# ---------------------------------------------------------------------------
# Guess handling
# ---------------------------------------------------------------------------

def submit_guess(guess: str):
    """
    Submit a guess and update the game, solver, and history.
    """
    # Validate before touching any state, so a rejected guess changes nothing.
    BullsAndCowsGame.validate_guess(guess)

    entropy_before = strategy.calc_game_entropy()
    expected_information = strategy.calc_guess_entropy(guess)

    bulls, cows = game.make_guess(guess)

    strategy.set_guess(guess)
    strategy.record_turn_feedback(
        bulls,
        cows,
    )

    actual_information = entropy_before - strategy.calc_game_entropy()

    history.append(
        {
            "Guess": guess,
            "🐂 Bulls": bulls,
            "🐄 Cows": cows,
            "Expected info (bits)": expected_information,
            "Actual info (bits)": actual_information,
        }
    )

    if game.game_state == GameState.WON:
        st.session_state.celebrate = True


def current_suggestions() -> list[tuple[str, float]]:
    """
    The solver's top guesses for the current turn.

    Computed once per turn: the page reruns on every interaction, and
    recomputing would reshuffle the first-turn suggestions each time.
    """
    cached = st.session_state.suggestions

    if cached is None or cached[0] != game.guess_count:
        cached = (game.guess_count, strategy.generate_top_guesses())
        st.session_state.suggestions = cached

    return cached[1]


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

header_left, header_right = st.columns([4, 1], vertical_alignment="center")

with header_left:
    st.title("🐂 Bulls & Cows")
    st.caption(
        "Guess the secret 4-digit number. 🐂 bull = right digit in the right "
        "place, 🐄 cow = right digit in the wrong place."
    )

with header_right:
    st.button(
        "🔄 New game",
        width="stretch",
        on_click=new_game,
    )


# ---------------------------------------------------------------------------
# Win message
# ---------------------------------------------------------------------------

if game.game_state == GameState.WON:
    st.success(
        f"🎉 You solved it in {game.guess_count} guesses! The secret was **{game.secret}**."
    )

    # `celebrate` is set when a game is won, so the balloons fly once per win.
    # Without the flag they would fly again on every rerun while the win
    # message is showing, e.g. when toggling "Show secret".
    if st.session_state.celebrate:
        st.balloons()
        st.session_state.celebrate = False


# ---------------------------------------------------------------------------
# Status: how much uncertainty is left
# ---------------------------------------------------------------------------

remaining = len(strategy.remaining_possibilities)
bits_left = strategy.calc_game_entropy()
bits_gained = strategy.initial_entropy - bits_left

guesses_col, remaining_col, bits_col = st.columns(3)
guesses_col.metric("Guesses", game.guess_count)
remaining_col.metric("Possibilities left", f"{remaining:,}")
bits_col.metric("Uncertainty", f"{bits_left:.2f} bits")

st.progress(
    bits_gained / strategy.initial_entropy,
    text=f"Information gained: {bits_gained:.2f} of {strategy.initial_entropy:.2f} bits",
)


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

hints_toggle_col, secret_toggle_col = st.columns(2)
show_hints = hints_toggle_col.toggle("Show hints", value=True)
show_secret = secret_toggle_col.toggle("Show secret", value=False)

if show_secret:
    st.info(f"🤫 The secret is **{game.secret}**")


# ---------------------------------------------------------------------------
# Guess input and hints, side by side
# ---------------------------------------------------------------------------

if game.game_state == GameState.IN_PROGRESS:
    guess_col, hints_col = st.columns(2, gap="large")

    with guess_col:
        with st.form("guess_form", clear_on_submit=True, border=False):
            guess = st.text_input(
                "Your guess",
                max_chars=4,
                placeholder="1234",
            )

            submitted = st.form_submit_button(
                "Guess",
                type="primary",
                width="stretch",
            )

        if submitted:
            try:
                submit_guess(guess.strip())
                st.rerun()

            except RuntimeError as error:
                st.error(str(error))

    if show_hints:
        with hints_col:
            st.caption("Hints: expected information. Click one to play it.")

            for suggested_guess, expected_bits in current_suggestions():
                st.button(
                    f"{suggested_guess} · {expected_bits:.2f} bits",
                    key=f"suggested_guess_{suggested_guess}",
                    width="stretch",
                    on_click=submit_guess,
                    args=(suggested_guess,),
                )


# ---------------------------------------------------------------------------
# Guess history
# ---------------------------------------------------------------------------

st.subheader("Guess history")

if history:
    history_table = pd.DataFrame(history)
    history_table.index = range(1, len(history_table) + 1)

    st.table(
        history_table.style.format(
            {
                "Expected info (bits)": "{:.2f}",
                "Actual info (bits)": "{:.2f}",
            }
        )
    )
    st.caption(
        "Expected info: what the guess gains on average, over all remaining "
        "secrets. Actual info: what it gained for this secret."
    )
else:
    st.caption("Your guesses and feedback will appear here.")
