# Sub game: review notes

Working reference, not the backlog (that's `TASKS.md`). First review
2026-09-29; status updated 2026-10-05, after the move into modules and the
Streamlit page.

## Still open

### Strategy behaviour
1. **Entropy stalls when it is already certain.** In a lost noisy-sensor game,
   the map was 100% on the sub's square, yet the strategy pinged (0, 0) 22 times
   in its last 50 pings and the sub's square only once. When the map is
   certain, every ping has about 0 expected information gain, so `argmax` falls
   back to the first square. Information gain has no reason to "confirm" a
   square, and winning requires it. Fix candidates (the hybrid): switch to
   MostLikely when `map.max()` is above a threshold, or when the best
   information gain is about 0.
2. **Lost games are excluded from the means.** `display_results` (notebook) and
   the page's advisor comparison average only the won games, so a strategy that
   loses games looks better than it is (Entropy's 96.6 on the noisy sensor
   left out 39 lost games). Show the lost count next to the mean, or count a
   lost game as `max_turns`.

### Code structure
3. **The belief update reaches the spec through the sensor**
   (`self.sensor.sensor_spec` in `BayesGameState`). The game state could hold
   the spec directly, which a spec-mismatch experiment also needs.
4. **No tests yet.** `tests/` is empty. Ready-made cases: the distance asserts
   (notebook cell 3), the four-square example for `get_new_belief_map` (Det and
   ND numbers in `bayes_search_explained.md`), and `detect_grid` against
   `calc_p`. Then delete the commented-out test in notebook cell 5.
5. **Unused `self.name` on every strategy.** Nothing reads it any more; the
   experiment and page dicts supply display names.
6. **Two Bayes updates.** `BayesGameState.get_new_belief_map` (one ping) and the
   4D version in `EntropyBasedStrategy` (all pings) do the same maths. A shared
   `bayes_update(likelihood, prior)` and `entropy(p, axis)` would also serve
   Bulls & Cows (TASKS.md cross-topic item).
7. **`PingSensor` takes the whole map but only uses its shape.**

### Minor
8. **`map` shadows the built-in** in `GameSimulator(map=...)` / `self.map` and
   `sample_map_for_sub_location(map)`.
9. **The notebook's Streamlit mockup (cell 13)** is superseded by the page and
   still has two bugs: it plays against `sub_location` (a leftover from cell 7)
   instead of `sub_true_location`, and it prints the whole information gain
   map as "bits". Fix it, or delete it.
10. `display_results` (notebook cell 9) is indented with 6 spaces; empty cells
    14 and 15.

## Resolved
- Non-square maps broke the update; swapped likelihood arguments; wrong
  docstring numbers; the unfair perfect-sensor baseline.
- Sensor and spec separated (`PingSensorSpec` vs `PingSensor`).
- Unseeded runs: kept unseeded on purpose. Fairness comes from sharing the map
  and sub locations across strategies.
- Slow loops: `detect_grid`, the vectorised update and the 4D table.
- Strategies return just the location; the `PingStrategy` Protocol uses
  `ProbMap`; `_play_game` is typed `int | None`.
- Reference loop code (`_get_new_belief_map_loop`, the old map loops) removed.
- Plotting split: `map_figure` in `ui/figures.py`, `map_utils.py` is pure numpy.

## Results to keep in mind (1000 games, 10×15 blob map)
- **Default sensor:** MostLikely 47.6 ± 1.3, Entropy 48.9 ± 1.4. No real
  difference.
- **Uniform prior:** both get only slightly slower (51.0, 52.7).
- **Noisy sensor** (0.5 / 0.3): MostLikely 71.4, Entropy 96.6 with 39 lost (see
  1). The prediction that a stronger neighbour signal would help Entropy was
  wrong.
- **Random should not depend on the prior at all**, yet it got 116.4 ± 3.0
  (correct prior) vs 107.1 ± 2.9 (uniform prior), about 2.2σ apart. Probably
  chance; worth rerunning once as a sanity check.
