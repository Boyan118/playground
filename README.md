## Prerequisites

- Python 3.11+
- uv

## From an empty project

```bash
uv sync
```

## Start the app

Run the project as a module:

```bash
cd /home/boyan/repos_github/playground
uv run python -m playground_package
```

Or run the Streamlit script directly:

```bash
cd /home/boyan/repos_github/playground
uv run streamlit run src/playground_package/streamlit_app/main.py
```
