
import streamlit as st

from playground_package.bulls_and_cows.code.bulls_and_cows_game import (
    BullsAndCowsGame,
    GameState,
)

st.title("🐂 Bulls & Cows")

if "game" not in st.session_state:
    st.session_state.game = BullsAndCowsGame()
    st.session_state.history = []

game = st.session_state.game

st.write(f"Guesses: {game.secret}")
st.write(f"Guesses: {game.guess_count}")

guess = st.text_input(
    "Enter your guess",
    max_chars=4
)


if st.button("Guess"):
    try:
        bulls, cows = game.make_guess(guess)

        st.session_state.history.append((guess, bulls, cows))

        if game.game_state == GameState.WON:
            st.success("You won!")

        for guess, bulls, cows in reversed(st.session_state.history):
            st.write(f"Guess: {guess} | 🐂 Bulls: {bulls} | 🐄 Cows: {cows}")


    except RuntimeError as e:
        st.error(str(e))