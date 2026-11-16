# Contributing

Thanks for improving gitglance! 🎉

## Setup

```bash
git clone https://github.com/kevindepro10-cool/gitglance.git
cd gitglance
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

The test suite builds small throwaway git repositories in temporary
directories (`tests/conftest.py`) — it never touches your own repos.

## Guidelines

- **Zero runtime dependencies** — the standard library is enough. Dev
  dependencies (`pytest`) live in `[project.optional-dependencies]`.
- **Python ≥ 3.9** — code uses `from __future__ import annotations`, so modern
  type syntax stays safe.
- **Style** — plain, typed, documented code; no comments unless truly needed.
- **Tests** — every new command or analysis function needs coverage.
- **Commits** — short imperative subject lines (`feat:`, `fix:`, `docs:`, ...).

## Workflow

1. Fork / create a feature branch
2. Make your change + tests
3. `pytest` must pass
4. Open a pull request describing what and why
