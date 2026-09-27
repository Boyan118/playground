# Tasks

## Now

### Project cleanup
- [x] Delete the stray `=4.2.0` file at the repo root
- [x] Move `ruff` and `ipykernel` to the `dev` dependency group; declare `numpy` explicitly
- [x] Update the README: Python version (3.14), what `python -m playground_package` runs, how to start the app
- [x] Remove leftovers: `streamlit_app/pages/01. bulls_and_cows.py`, `calculator/` and its test, `main()` in `__init__.py`
- [ ] Move `notebooks/*` into their topic packages and remove the `notebooks/` folder
- [x] Strip notebook outputs (e.g. `nbstripout` as a git filter); `plant.ipynb` is 7 MB
- [ ] Update `.gitignore`: old `notebooks/stats/*.pkl` paths → topic `data/` folders; stop ignoring the space game's `assets`

### Bulls & Cows
- [x] Build file paths from `Path(__file__)` in `ui/page.py` (no longer needed: the page loads no files)
- [x] Replace the 405 MB dict-of-dicts pickle with a 9000×9000 numpy `uint8` table (~81 MB, encoding `bulls*5 + cows`), or compute it at startup
- [ ] (me, learn) Debug `feedback_table.py` to understand the implementation, then remove the first-turn special case (`best_opening_guesses` and the `turns_counter == 1` branch in `EntropyStrategy`) if it's no longer needed

## Later

### Bulls & Cows
- [x] Guesses with non-digits crash the page (`IndexError`); validate in `make_guess`
- [x] `random.shuffle` mutates the candidates list shared by `st.cache_resource`
- [ ] Remove the duplicated `reduce_set` and the unused `GameState.LOST`
- [ ] Consider guesses outside the consistent set (Knuth-style)
- [ ] Compare max-entropy with minimax and with minimising the expected remaining set size
- [ ] Benchmark: run each strategy over all 9000 secrets and plot the guess-count distribution
- [x] Avoid recomputing top guesses on every Streamlit rerun


### Cross-topic
- [ ] Shared entropy / information-gain helpers used by the sub game and Bulls & Cows
