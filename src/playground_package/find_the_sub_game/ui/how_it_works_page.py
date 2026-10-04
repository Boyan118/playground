from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Find the Sub: how it works",
    page_icon="📖",
    layout="centered",  # a narrow column reads better for long text
)

# The explainer lives next to the notebooks, so the notebook and the app share it.
# It's read on every run, so edits to the markdown show up without a restart.
BAYES_EXPLAINER = Path(__file__).parent.parent / "notebooks" / "bayes_search_explained.md"

st.page_link("../find_the_sub_game/ui/page.py", label="Back to the game", icon="🚢")

st.markdown(BAYES_EXPLAINER.read_text())
