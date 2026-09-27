# Playground

A collection of experiments and small games for exploring concepts hands-on.
Each topic lives in its own package under `src/playground_package/`.

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)

## Setup

After cloning (the devcontainer does this automatically):

```bash
uv sync
uv run nbstripout --install --attributes .gitattributes
```

The second command registers a git filter that strips notebook outputs
(plots, printed results) from what gets committed; your local notebooks keep
them. It's stored in `.git/config`, which isn't cloned, so run it once per
clone, and again if you recreate `.venv`.

## Streamlit app

The Streamlit app hosts the interactive topic pages (currently Bulls & Cows):

```bash
uv run streamlit run src/playground_package/streamlit_app/main.py
```

## Space game

Running the package as a module starts the pygame space game:

```bash
uv run python -m playground_package
```

It expects a background image at `src/playground_package/space_game/assets/bg.jpeg`.

## Development

```bash
uv run pytest
uv run ruff check .
```
