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

## Workflow and layout
- Each topic is a package: `src/playground_package/<topic>/` holding its
  notebooks, code, data and Streamlit `page.py`.
- I start every idea in a notebook and move code into modules later, once it
  has settled. Don't push extraction early.
- `src/playground_package/streamlit_app/main.py` registers the topic pages.
- Backlog: @TASKS.md

## Commands
- `uv sync`, `uv run pytest`, `uv run ruff check .`
- App: `uv run streamlit run src/playground_package/streamlit_app/main.py`

## Conventions
- Python 3.14, uv, ruff.
- Build file paths from `Path(__file__)`, never from the working directory.
- Don't commit large data files or notebook outputs.
