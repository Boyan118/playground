from functools import partial

import numpy as np
import pandas as pd
import streamlit as st

from playground_package.find_the_sub_game.code.bayes_game_state import BayesGameState
from playground_package.find_the_sub_game.code.map_utils import (
    generate_gaussian_blob_map,
    generate_inverted_map,
    generate_uniform_map,
    sample_map_for_sub_location,
)
from playground_package.find_the_sub_game.code.sensors import (
    PingResult,
    PingSensor,
    PingSensorSpec,
)
from playground_package.find_the_sub_game.code.simulation import GameSimulator
from playground_package.find_the_sub_game.code.strategies import (
    EntropyBasedStrategy,
    MostLikelySquareStrategy,
)
from playground_package.find_the_sub_game.code.types import ProbMap
from playground_package.find_the_sub_game.ui.figures import map_figure

st.set_page_config(
    page_title="Find the Sub",
    page_icon="🚢",
    layout="wide",
)

SENSOR_SPEC = PingSensorSpec()

BOARD_SIZES = {
    "Small (6 × 8)": (6, 8),
    "Medium (10 × 15)": (10, 15),
    "Large (15 × 20)": (15, 20),
}

# option: (label, caption shown under it)
HYPOTHESES = {
    "Correct": ("Correct: I know where subs hide", "Your map is the real intel the sub was hidden by."),
    "None": ("None: I have no idea", "Your map starts flat: every square equally likely."),
    "Wrong": ("Wrong: my intel is misleading", "Your map is upside down: it points away from the sub."),
}

COMPARISON_GAMES = 100




# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

@st.cache_resource
def load_entropy_strategy(shape: tuple[int, int]) -> EntropyBasedStrategy:
    # One instance per board size, shared across sessions: it only keeps the
    # likelihood table, which depends on the board shape and the sensor spec.
    return EntropyBasedStrategy(SENSOR_SPEC)


most_likely_strategy = MostLikelySquareStrategy()


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------
# st.session_state is shared by all pages of the app, so every key here starts
# with "sub_" to stay clear of the Bulls & Cows page.

def new_game():
    """A new world (real map and sub location), then a fresh game on it."""
    shape = BOARD_SIZES[st.session_state.get("sub_board_size", "Small (6 × 8)")]

    # The truth: where subs really hide. The sub is drawn from this map.
    true_map = generate_gaussian_blob_map(*shape)
    st.session_state.sub_true_map = true_map
    st.session_state.sub_location = tuple(int(i) for i in sample_map_for_sub_location(true_map))

    restart_game()


def restart_game():
    """Start over in the same world with the selected hypothesis.

    Same real map and sub location, a new starting belief and 0 pings, so
    switching hypotheses shows what each one does to the map you play on.
    """
    true_map = st.session_state.sub_true_map
    sub_location = st.session_state.sub_location
    shape = true_map.shape
    hypothesis = st.session_state.get("sub_hypothesis", "Correct")

    # The belief the player starts from.
    match hypothesis:
        case "Correct":
            start_map = true_map
        case "None":
            start_map = generate_uniform_map(*shape)
        case "Wrong":
            start_map = generate_inverted_map(true_map)

    sensor = PingSensor(sub_location, start_map, sensor_spec=SENSOR_SPEC)

    st.session_state.sub_game = BayesGameState(sub_location, start_map, sensor)
    st.session_state.sub_start_map = start_map
    st.session_state.sub_history = []
    st.session_state.sub_last_ping = None
    # Uncertainty in bits at the start and after each ping
    st.session_state.sub_entropy_trail = [float(entropy_strategy_for(start_map).calc_entropy(start_map))]
    st.session_state.sub_won = False
    st.session_state.sub_celebrate = False
    st.session_state.sub_comparison = None


def entropy_strategy_for(map_arr: ProbMap) -> EntropyBasedStrategy:
    return load_entropy_strategy(map_arr.shape)


if "sub_game" not in st.session_state:
    new_game()

# session_state values are untyped; annotate them to get type checking and
# autocompletion back.
game: BayesGameState = st.session_state.sub_game
true_map: ProbMap = st.session_state.sub_true_map
start_map: ProbMap = st.session_state.sub_start_map
history: list[dict] = st.session_state.sub_history
entropy_trail: list[float] = st.session_state.sub_entropy_trail
won: bool = st.session_state.sub_won

entropy_strategy = entropy_strategy_for(game.map_array)


# ---------------------------------------------------------------------------
# Advisors
# ---------------------------------------------------------------------------

def advice(belief: ProbMap) -> tuple[tuple[int, int], tuple[int, int], np.ndarray]:
    """Most likely square, the entropy strategy's square, and the information gain map."""
    most_likely = tuple(int(i) for i in most_likely_strategy.choose_location(belief))
    entropy_location, information_gain = entropy_strategy.choose_location_detailed(belief)
    return most_likely, tuple(int(i) for i in entropy_location), information_gain


# ---------------------------------------------------------------------------
# Ping handling
# ---------------------------------------------------------------------------

def ping(location: tuple[int, int]):
    """Ping a square and update the game, the uncertainty trail and the history."""
    if st.session_state.sub_won:
        return

    belief_before = game.map_array
    most_likely, entropy_choice, _ = advice(belief_before)

    result = game.advance_state(location)

    entropy_after = float(entropy_strategy.calc_entropy(game.map_array))
    information_gained = entropy_trail[-1] - entropy_after
    entropy_trail.append(entropy_after)
    st.session_state.sub_last_ping = location

    matches = [name for name, square in [("Most likely", most_likely), ("Entropy", entropy_choice)] if square == location]

    history.append(
        {
            "Square": f"({location[0]}, {location[1]})",
            "Outcome": "📡 Detect" if result.ping_outcome == PingResult.DETECTED else "No detect",
            "P(sub here) before": float(result.pinged_location_prob),
            "Info gained (bits)": information_gained,
            "Uncertainty after (bits)": entropy_after,
            "Advisor": " + ".join(matches) or "—",
        }
    )

    if result.game_won:
        st.session_state.sub_won = True
        st.session_state.sub_celebrate = True


def on_map_click(chart_key: str):
    """Ping the clicked square. Any trace's point sits on a cell centre: x = column, y = row."""
    points = st.session_state[chart_key].selection.points
    if points:
        ping((round(points[0]["y"]), round(points[0]["x"])))


def compare_with_advisors():
    """Average pings of both advisors on this game's maps, for the end-of-game comparison."""
    trials = [sample_map_for_sub_location(true_map) for _ in range(COMPARISON_GAMES)]
    simulator = GameSimulator(map=start_map, trials=trials, sensor_spec=SENSOR_SPEC)

    st.session_state.sub_comparison = {
        "Most likely": simulator.run(lambda spec: most_likely_strategy),
        "Entropy": simulator.run(lambda spec: entropy_strategy),
    }


# ---------------------------------------------------------------------------
# Map figure
# ---------------------------------------------------------------------------

def show_map(values, value_label, value_format, chart_key, **markers):
    st.plotly_chart(
        map_figure(values, value_label, value_format, **markers),
        key=chart_key,
        on_select=partial(on_map_click, chart_key),
        selection_mode="points",
        config={"displayModeBar": False},
    )


# ---------------------------------------------------------------------------
# Layout (see CLAUDE.md): header row; controls on the left, the game in the
# centre, less important metrics on the right.
# ---------------------------------------------------------------------------

# Controls on the left; on the right the header, then the game and its metrics
controls_col, content_col = st.columns([1, 4], gap="large")


# ---------------------------------------------------------------------------
# Controls column (left): controls that restart the game, then those that don't
# ---------------------------------------------------------------------------

with controls_col:
    # Restart the game
    with st.container(border=True):
        st.selectbox(
            "Board size",
            BOARD_SIZES,
            index=0,  # Small, the same default new_game() falls back to
            key="sub_board_size",
            on_change=new_game,
        )
        hypothesis = st.radio(
            "Your hypothesis",
            HYPOTHESES,
            format_func=lambda option: HYPOTHESES[option][0],
            key="sub_hypothesis",
            on_change=restart_game,
        )
        st.caption(HYPOTHESES[hypothesis][1])  # only the selected option's explanation

        st.button("🔄 New game", width="stretch", on_click=new_game)

    # Don't restart the game: they only change what you see
    with st.container(border=True):
        show_advisors = st.toggle("Show advisors", value=True)
        show_sub = st.toggle("Show the sub", value=False)


# ---------------------------------------------------------------------------
# Header (above the centre and right columns)
# ---------------------------------------------------------------------------

with content_col:
    # Header across the game and its metrics, so the metrics start level with the game.
    # The same [3, 1] split as below puts the button above the metrics column.
    # Aligned to the top, so the button stays level with the title, not with the text below it
    title_col, how_it_works_col = st.columns([3, 1], gap="large", vertical_alignment="top")
    title_col.title("🚢 Find the Sub")
    title_col.markdown(
        f"Click a square to ping it. A ping on the sub's square detects it "
        f"{SENSOR_SPEC.p_hit:.0%} of the time, and that wins. A ping next to the sub "
        f"gives a false alarm {SENSOR_SPEC.p_near:.0%} of the time, further away "
        f"{SENSOR_SPEC.p_far:.1%}. After every ping, the map updates with Bayes' rule."
    )
    if how_it_works_col.button("📖 How it works", width="stretch"):
        st.switch_page("../find_the_sub_game/ui/how_it_works_page.py")

    main_col, info_col = st.columns([3, 1], gap="large")


# ---------------------------------------------------------------------------
# Info column (right): less important metrics about the game
# ---------------------------------------------------------------------------

with info_col:
    st.metric("Pings", len(history), border=True)

    bits_delta = f"{entropy_trail[-1] - entropy_trail[-2]:.2f} bits" if len(entropy_trail) > 1 else None
    st.metric(
        "Uncertainty",
        f"{entropy_trail[-1]:.2f} bits",
        delta=bits_delta,
        delta_color="inverse",  # a decrease is good news, so show it in green
        chart_data=entropy_trail,
        chart_type="area",
        border=True,
        help="Entropy of your current map: how many yes/no questions' worth of "
             "uncertainty is left about where the sub is.",
    )


# ---------------------------------------------------------------------------
# Main column (centre): what you do to play and the map; history below
# ---------------------------------------------------------------------------

# The play area in one box: advisors, maps and the history of your pings
with main_col.container(border=True):
    sub_location = game.sub_location if (show_sub or won) else None
    last_ping = st.session_state.sub_last_ping

    if won:
        st.success(f"🎉 Found it in {len(history)} pings! The sub was at {game.sub_location}.")

        # Balloons once per win, not on every rerun while the message shows.
        if st.session_state.sub_celebrate:
            st.balloons()
            st.session_state.sub_celebrate = False

        comparison = st.session_state.sub_comparison
        if comparison is None:
            if st.button(f"How would the advisors do on this map? ({COMPARISON_GAMES} games each)"):
                with st.spinner("Simulating..."):
                    compare_with_advisors()
                st.rerun()
        else:
            your_pings = len(history)
            you_col, *advisor_cols = st.columns(3)
            you_col.metric("You", f"{your_pings} pings", border=True)
            for column, (name, pings) in zip(advisor_cols, comparison.items()):
                # A lost game (None, hit the turn cap) took longer than any won game,
                # so it counts as max_turns: you beat it.
                lengths = np.array([p if p is not None else np.inf for p in pings])

                # Your percentile: the share of its games that took more pings than
                # yours, with ties counted as half a win.
                beaten = np.mean(lengths > your_pings) + 0.5 * np.mean(lengths == your_pings)

                column.metric(
                    f"{name} (median)",
                    f"{np.median(lengths):.0f} pings",
                    help=f"Over {len(pings)} games on the same maps. Game lengths have a long tail, "
                         f"so the median is the typical game; the mean is "
                         f"{np.mean(lengths[np.isfinite(lengths)]):.0f} pings (won games only).",
                    border=True,
                )
                column.caption(f"You beat **{beaten:.0%}** of its games.")

        most_likely = entropy_choice = None
        information_gain = None
    else:
        most_likely, entropy_choice, information_gain = advice(game.map_array)

        if show_advisors:
            ml_col, entropy_col = st.columns(2, gap="large")

            p_win = SENSOR_SPEC.p_hit * game.map_array[most_likely]
            ml_col.button(
                f"🟠 Most likely: ping {most_likely}",
                width="stretch",
                on_click=ping,
                args=(most_likely,),
            )
            ml_col.caption(
                f"Best chance to win now: {SENSOR_SPEC.p_hit:.0%} × "
                f"{game.map_array[most_likely]:.1%} = **{p_win:.1%}**"
            )

            entropy_col.button(
                f"🟢 Entropy: ping {entropy_choice}",
                width="stretch",
                on_click=ping,
                args=(entropy_choice,),
            )
            entropy_col.caption(
                f"Most to learn: expected **{information_gain[entropy_choice]:.2f} bits** of information"
            )

    if not show_advisors:
        most_likely = entropy_choice = None

    markers = {
        "most_likely": most_likely,
        "entropy_choice": entropy_choice,
        "last_ping": last_ping,
        "sub_location": sub_location,
    }

    # A new chart key every turn gives a fresh selection, so the same square
    # can be clicked twice in a row.
    belief_tab, information_tab = st.tabs(["Where is the sub?", "Where would a ping teach most?"])
    with belief_tab:
        show_map(game.map_array, "P(sub here)", ".1%", f"sub_belief_map_{len(history)}", **markers)
    with information_tab:
        if information_gain is None:
            st.caption("The game is over: nothing left to learn.")
        else:
            show_map(information_gain, "Info gain (bits)", ".3f", f"sub_information_map_{len(history)}", **markers)
            st.caption(
                "Expected information gain of pinging each square: how much a ping "
                "there would reduce the uncertainty, on average over Detect and No detect."
            )

    st.subheader("Ping history")

    if history:
        history_table = pd.DataFrame(history)
        history_table.index = range(1, len(history_table) + 1)

        st.table(
            history_table.style.format(
                {
                    "P(sub here) before": "{:.1%}",
                    "Info gained (bits)": "{:.2f}",
                    "Uncertainty after (bits)": "{:.2f}",
                }
            )
        )
        st.caption(
            "Info gained: how much this ping's outcome reduced the uncertainty. It can be "
            "negative: a surprising result can make the map less certain."
        )
    else:
        st.caption("Your pings will appear here.")
