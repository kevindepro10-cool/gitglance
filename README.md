<div align="center">

# gitglance

**Analyze any git repository at a glance — contributors, activity, hotspots and stale branches.**

Zero runtime dependencies · Python ≥ 3.9 · MIT

</div>

---

## Why

`git log` tells you everything and shows you nothing. `gitglance` turns your
repository's history into a few crisp, colorful terminal reports:

- **`summary`** — commits, authors, tracked files, HEAD and a language breakdown
- **`authors`** — contributor leaderboard with line stats (+/−)
- **`activity`** — commits per week (ASCII bars + heatmap) or by weekday
- **`hotspots`** — the files your team touches most (a.k.a. future bugs)
- **`stale`** — branches nobody has touched in weeks

## Install

```bash
pip install .
```

Requires only Python ≥ 3.9 and a `git` executable on `PATH`. No third-party
runtime dependencies.

## Usage

```bash
gitglance summary                 # overview of the repo you are in
gitglance authors -n 5            # top 5 contributors
gitglance activity -w 26          # last 26 weeks of commit activity
gitglance activity --by-weekday   # when does your team actually commit?
gitglance hotspots -n 15          # 15 most-changed files
gitglance stale -d 60             # branches untouched for 60+ days
gitglance -C ~/src/myproject summary   # analyze any repo from anywhere
```

Use `--no-color` (or set `NO_COLOR`) to disable ANSI colors.

## Example

```
gitglance · repository summary

  Path:      /home/dev/gitglance
  Branch:    main
  Commits:   214
  Authors:   6
  Tracked:   48 files
  First:     2024-01-15 10:00
  Last:      2025-06-02 18:34 (today)

  HEAD:       a1b2c3d4 feat: add stale-branch detection

  Languages
    Python         ████████████████████  84.2%  22 files
    Markdown       ███                    9.1%  4 files
    TOML           █                      3.4%  1 files
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
