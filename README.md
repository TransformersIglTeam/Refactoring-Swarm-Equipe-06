# Refactoring-Swarm-Equipe-06

This repository contains tools for the project.

## Running tests

We use pytest for unit tests. To run the tests locally:

1. Create and activate a Python virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

3. Run pytest:

```bash
pytest -q
```

Notes:
- Tests include a small stub for `langchain.tools.BaseTool` so you don't need the full `langchain` package installed to run the unit tests.
- If you encounter missing `pytest` install it with `pip install pytest`.
