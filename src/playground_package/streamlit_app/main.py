import sys
from pathlib import Path

import streamlit as st

# Make `playground_package` importable even if the host only installs the
# dependencies and not the project itself (e.g. Streamlit Community Cloud).
# parents[2] is the `src` directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# A dict groups the pages under a heading per topic in the sidebar.
pg = st.navigation({
    "Bulls & Cows": [
        st.Page(
            "../bulls_and_cows/ui/page.py",
            title="Bulls & Cows",
            url_path="bulls-and-cows",
            icon="🐂",
        ),
    ],
    "Find the Sub": [
        st.Page(
            "../find_the_sub_game/ui/page.py",
            title="Find the Sub",
            url_path="find-the-sub",
            icon="🚢",
        ),
        st.Page(
            "../find_the_sub_game/ui/how_it_works_page.py",
            title="How it works",
            url_path="find-the-sub-how-it-works",
            icon="📖",
        ),
    ],
})

pg.run()
