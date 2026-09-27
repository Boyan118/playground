import streamlit as st

pg = st.navigation([
    st.Page(
        "../bulls_and_cows/ui/page.py",
        title="Bulls & Cows",
        icon="🐂",
    ),
])

pg.run()