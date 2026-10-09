import sys
from pathlib import Path

import streamlit as st

# Make `playground_package` importable even if the host only installs the
# dependencies and not the project itself (e.g. Streamlit Community Cloud).
# parents[2] is the `src` directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

pg = st.navigation([
    st.Page(
        "../bulls_and_cows/ui/page.py",
        title="Bulls & Cows",
        url_path="bulls-and-cows",
        icon="🐂",
    ),
    # Not in the menu: reached from the "How it works" button on the Bulls & Cows page
    st.Page(
        "../bulls_and_cows/ui/how_it_works_page.py",
        title="Bulls & Cows: how it works",
        url_path="bulls-and-cows-how-it-works",
        icon="📖",
        visibility="hidden",
    ),
    st.Page(
        "../find_the_sub_game/ui/page.py",
        title="Find the Sub",
        url_path="find-the-sub",
        icon="🚢",
    ),
    # Not in the menu: reached from the "How it works" button on the Find the Sub page
    st.Page(
        "../find_the_sub_game/ui/how_it_works_page.py",
        title="Find the Sub: how it works",
        url_path="find-the-sub-how-it-works",
        icon="📖",
        visibility="hidden",
    ),
])

pg.run()
