# Playground

A personal playground for understanding concepts through experiments and small
games. The goal is **my understanding**, not finished software.

## How to work with me
For each task I say which mode I want. If I don't, ask.

- **chore**: just do it, then briefly say what changed.
- **explain**: do it, but explain the what and why as you go. I know the
  topic and want a refresher, so be concise and skip the basics.
- **learn**: teacher mode. I write the code; you explain concepts, ask guiding
  questions, and review what I wrote. When I'm stuck, give a hint first, then a
  stronger hint, and the solution only if I ask for it. Point out bugs and
  wrong math directly, but let me fix them.

In every mode: suggest a natural next experiment if there is one, but don't
expand the scope of the task.

Never stage, commit or push unless I explicitly ask. I review, stage and
commit changes myself. Use `rm`, not `git rm`.

Work happens on the `playground` branch. `main` is the stable branch the app
deploys from: never commit to it, merge into it or push to it unless I ask.

When reporting what you did, show the commands you ran where they're useful
(e.g. `uv add --dev ruff`), so I can learn them and repeat them.

## Workflow and layout
- Each topic is a package: `src/playground_package/<topic>/` holding its
  notebooks, code, data and Streamlit `page.py`.
- I start every idea in a notebook and move code into modules later, once it
  has settled. Don't push extraction early.
- Backlog: @TASKS.md

## Streamlit pages
- Register each topic page in `src/playground_package/streamlit_app/main.py`
  via `st.navigation`.
- Follow the Bulls & Cows page (`bulls_and_cows/ui/page.py`) as the reference:
  game logic lives in the topic's `code/`, the page only displays it;
  typed `session_state` values; heavy data under `st.cache_resource`.
- Check pages headlessly with `streamlit.testing.v1.AppTest` before calling a
  UI change done.
- Deployed on Streamlit Community Cloud
  (https://playground-fyhdqyovygsy7owe5igt9z.streamlit.app/) from `main`,
  Python 3.14. Every push to `main` redeploys; I publish with
  `git push origin playground:main`.

## Commands
- `uv sync`, `uv run pytest`, `uv run ruff check .`
- App: `uv run streamlit run src/playground_package/streamlit_app/main.py`

## Conventions
- Python 3.14, uv, ruff.
- Build file paths from `Path(__file__)`, never from the working directory.
- Don't commit large data files or notebook outputs.
