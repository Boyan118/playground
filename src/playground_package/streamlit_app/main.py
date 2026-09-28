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
        icon="🐂",
    ),
])

pg.run()
