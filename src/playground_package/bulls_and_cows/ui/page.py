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
    layout="wide",
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
    # (possibilities left, uncertainty in bits) at the start and after each guess
    st.session_state.status_trail = [
        (
            len(st.session_state.strategy.remaining_possibilities),
            st.session_state.strategy.initial_entropy,
        )
    ]
    st.session_state.suggestions = None
    st.session_state.celebrate = False


if "game" not in st.session_state:
    new_game()

# session_state values are untyped; annotate them to get type checking and
# autocompletion back.
game: BullsAndCowsGame = st.session_state.game
strategy: EntropyStrategy = st.session_state.strategy
history: list[dict] = st.session_state.history
status_trail: list[tuple[int, float]] = st.session_state.status_trail


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

    entropy_after = strategy.calc_game_entropy()
    actual_information = entropy_before - entropy_after

    status_trail.append((len(strategy.remaining_possibilities), entropy_after))

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
# Layout
# ---------------------------------------------------------------------------

# The empty right column is a spacer that keeps the game area centred.
status_col, main_col, _ = st.columns([1, 3, 1], gap="large")


# ---------------------------------------------------------------------------
# Status column (left): display options and game state
# ---------------------------------------------------------------------------

with status_col:
    show_hints = st.toggle("Show hints", value=True)
    show_secret = st.toggle("Show secret", value=False)

    if show_secret:
        st.info(f"🤫 The secret is **{game.secret}**")

    (remaining, bits_left) = status_trail[-1]

    # Change since the previous guess; nothing to compare before the first one.
    if len(status_trail) > 1:
        (previous_remaining, previous_bits) = status_trail[-2]
        remaining_delta = f"{remaining - previous_remaining:,}"
        bits_delta = f"{bits_left - previous_bits:.2f} bits"
    else:
        remaining_delta = None
        bits_delta = None

    st.metric("Guesses", game.guess_count, border=True)

    # "inverse": a decrease is good news, so show it in green.
    st.metric(
        "Possibilities left",
        f"{remaining:,}",
        delta=remaining_delta,
        delta_color="inverse",
        border=True,
    )

    # The sparkline tracks bits rather than possibilities: each guess removes
    # a fraction of the possibilities, which shows up as a steady drop in bits.
    st.metric(
        "Uncertainty",
        f"{bits_left:.2f} bits",
        delta=bits_delta,
        delta_color="inverse",
        chart_data=[bits for (_, bits) in status_trail],
        chart_type="area",
        border=True,
    )


# ---------------------------------------------------------------------------
# Main column (centre): header, win message, guess input and hints, history
# ---------------------------------------------------------------------------

with main_col:
    # The header lives in the main column so it lines up with the game.
    title_col, new_game_col = st.columns([3, 1], vertical_alignment="center")
    title_col.title("🐂 Bulls & Cows")
    new_game_col.button(
        "🔄 New game",
        width="stretch",
        on_click=new_game,
    )

    st.caption(
        "Guess the secret 4-digit number. 🐂 bull = right digit in the right "
        "place, 🐄 cow = right digit in the wrong place."
    )

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
