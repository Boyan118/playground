import pickle

import streamlit as st

from playground_package.bulls_and_cows.code.bulls_and_cows_game import (
    BullsAndCowsGame,
    GameState,
)
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
def load_solver_data():
    with open(
        "src/playground_package/bulls_and_cows/data/entropy_9k.pkl",
        "rb",
    ) as f:
        entropy_9k = pickle.load(f)

    with open(
        "src/playground_package/bulls_and_cows/data/bulls_cows_9k.pkl",
        "rb",
    ) as f:
        bulls_cows_cache = pickle.load(f)

    candidates = sorted(
        entropy_9k,
        key=entropy_9k.get,
        reverse=True,
    )

    max_val = entropy_9k[candidates[0]]

    candidates = [
        str(candidate)
        for candidate in candidates
        if entropy_9k[candidate] == max_val
    ]

    return max_val, candidates, bulls_cows_cache


max_val, candidates, bulls_cows_cache = load_solver_data()


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------

if "game" not in st.session_state:
    st.session_state.game = BullsAndCowsGame()

if "history" not in st.session_state:
    st.session_state.history = []

if "strategy" not in st.session_state:
    st.session_state.strategy = EntropyStrategy(
        max_val,
        candidates,
        bulls_cows_cache,
    )


game = st.session_state.game
strategy = st.session_state.strategy


# ---------------------------------------------------------------------------
# Guess handling
# ---------------------------------------------------------------------------

def submit_guess(guess: str):
    """
    Submit a guess and update the game, solver, and history.
    """
    entropy_before = strategy.calc_game_entropy()

    strategy.set_guess(guess)

    bulls, cows = game.make_guess(guess)

    strategy.record_turn_feedback(
        bulls,
        cows,
    )

    entropy_after = strategy.calc_game_entropy()

    entropy_reduction = entropy_before - entropy_after

    st.session_state.history.append(
        {
            "Guess": guess,
            "Bulls": bulls,
            "Cows": cows,
            "Entropy reduction": entropy_reduction,
        }
    )


def select_suggested_guess(guess: str):
    """
    Automatically submit a suggested guess.
    """
    submit_guess(guess)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

header_left, header_right = st.columns([4, 1])

with header_left:
    st.title("🐂 Bulls & Cows")
    st.caption(
        "Guess the secret number and watch the solver narrow down "
        "the search space."
    )

with header_right:
    st.write("")

    if st.button(
        "🔄 New game",
        use_container_width=True,
    ):
        st.session_state.game = BullsAndCowsGame()
        st.session_state.history = []
        st.session_state.strategy = EntropyStrategy(
            max_val,
            candidates,
            bulls_cows_cache,
        )
        st.session_state.guess_input = ""
        st.rerun()


# ---------------------------------------------------------------------------
# Top status bar
# ---------------------------------------------------------------------------

st.divider()

guesses_col, space_col, solver_col = st.columns(
    [1, 1.5, 1.5],
    gap="large",
)


# ---------------------------------------------------------------------------
# Guesses + uncertainty
# ---------------------------------------------------------------------------

with guesses_col:
    st.metric(
        "Guesses",
        game.guess_count,
    )

    if game.game_state == GameState.IN_PROGRESS:
        entropy = strategy.calc_game_entropy()

        st.metric(
            "Uncertainty",
            f"{entropy:.2f} bits",
        )
    else:
        st.metric(
            "Status",
            "Solved 🎉",
        )


# ---------------------------------------------------------------------------
# Possibility space
# ---------------------------------------------------------------------------

with space_col:
    st.caption("Possibility space")

    if game.game_state == GameState.IN_PROGRESS:
        remaining = len(strategy.remaining_possibilities)

        # Outer square represents the original 9,000 possibilities.
        max_side = 150
        min_side = 8

        # Inner square area represents remaining possibilities.
        remaining_side = max(
            min_side,
            int(max_side * (remaining / 9000) ** 0.5),
        )

        st.markdown(
            f"""
            <div style="
                width: {max_side}px;
                height: {max_side}px;
                margin: 4px auto 8px auto;
                border: 2px solid rgba(128, 128, 128, 0.5);
                border-radius: 8px;
                display: flex;
                align-items: flex-end;
                justify-content: flex-start;
                overflow: hidden;
                background: rgba(128, 128, 128, 0.08);
            ">
                <div style="
                    width: {remaining_side}px;
                    height: {remaining_side}px;
                    background: rgba(255, 75, 75, 0.75);
                    border-radius: 5px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: 600;
                    font-size: 12px;
                    flex-shrink: 0;
                ">
                    {remaining:,}
                </div>
            </div>

            <div style="
                text-align: center;
                font-size: 12px;
                color: rgba(128, 128, 128, 0.9);
            ">
                {remaining:,} possibilities
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            """
            <div style="
                width: 150px;
                height: 150px;
                margin: 4px auto 8px auto;
                border: 2px solid rgba(128, 128, 128, 0.5);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(75, 180, 100, 0.25);
                color: rgba(75, 180, 100, 1);
                font-weight: 600;
            ">
                Solved 🎉
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Suggested guesses
# ---------------------------------------------------------------------------

with solver_col:
    st.caption("Suggested guesses")

    if game.game_state == GameState.IN_PROGRESS:
        proposed_moves = strategy.generate_top_guesses()

        for suggested_guess, average_entropy in proposed_moves:
            st.button(
                f"{suggested_guess} · {average_entropy:.4f} bits",
                key=f"suggested_guess_{suggested_guess}",
                use_container_width=True,
                on_click=select_suggested_guess,
                args=(suggested_guess,),
            )

    else:
        st.caption("Puzzle solved.")


# ---------------------------------------------------------------------------
# Main game
# ---------------------------------------------------------------------------

st.divider()

play_col, history_col = st.columns(
    [1, 1.4],
    gap="large",
)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

with play_col:
    st.subheader("Your guess")

    guess = st.text_input(
        "Enter a 4-digit number",
        max_chars=4,
        placeholder="1234",
        key="guess_input",
        disabled=game.game_state != GameState.IN_PROGRESS,
    )

    if st.button(
        "Submit guess",
        type="primary",
        use_container_width=True,
        disabled=game.game_state != GameState.IN_PROGRESS,
    ):
        try:
            submit_guess(guess)
            st.rerun()

        except RuntimeError as error:
            st.error(str(error))


# ---------------------------------------------------------------------------
# Guess history
# ---------------------------------------------------------------------------

with history_col:
    st.subheader("Guess history")

    if st.session_state.history:
        st.dataframe(
            st.session_state.history,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Entropy reduction": st.column_config.NumberColumn(
                    "Entropy ↓",
                    format="%.2f bits",
                ),
            },
        )
    else:
        st.caption(
            "Your guesses and feedback will appear here."
        )


# ---------------------------------------------------------------------------
# Win message
# ---------------------------------------------------------------------------

if game.game_state == GameState.WON:
    st.divider()

    st.success(
        f"🎉 You solved it in {game.guess_count} guesses!"
    )

    st.balloons()