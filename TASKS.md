# Tasks

## Now

### Project cleanup
- [ ] Move the control-theory notebook (`notebooks/control_theory/`) into a topic package and remove the `notebooks/` folder (the sub game is done; `notebooks/stats/` is empty)
- [ ] Update `.gitignore`: drop the old `notebooks/stats/*.pkl` lines; stop ignoring the space game's `assets`; decide on the global `docs` rule (it keeps `notebooks/control_theory/docs/` out of git)

### Bulls & Cows
- [ ] (me, learn) Debug `feedback_table.py` to understand the implementation, then remove the first-turn special case (`best_opening_guesses` and the `turns_counter == 1` branch in `EntropyStrategy`) if it's no longer needed

### Find the Sub
- [ ] Tests in `tests/`: distance checks, the four-square Bayes example (`bayes_search_explained.md`), `detect_grid` against `calc_p`
- [ ] Lost games are left out of the averages (notebook `display_results`, page comparison): show them or count them as `max_turns`

## Later

### Bulls & Cows

### Find the Sub
- [ ] (me, learn) Extend `find_the_sub_game/notebooks/bayes_search_explained.md` with entropy: initial entropy, expected entropy after a ping, information gain (same four-square example)
- [ ] Combined strategy: Can we combine MostLikely with information gain
- [ ] KL divergence: how good is my prior? KL(truth ‖ belief) = the extra bits you pay on average for believing q when the truth is p; 0 only when the belief matches the truth. Measured on 200 blob maps: correct 0, uniform ≈ 0.35, inverted ≈ 1.15 bits. Check it against simulated pings per prior (the inverted prior isn't simulated yet), and maybe show it on the page

## Future projects
- [ ] numpy exercise
- [ ] Hypothesis testing and A/B testing: review the maths, and compare with a Bayesian alternative (a Beta distribution per variant)
- [ ] Graph database: think of a playground project
