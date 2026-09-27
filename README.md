# Playground

A collection of experiments and small games for exploring concepts hands-on.
Each topic lives in its own package under `src/playground_package/`.

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

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
