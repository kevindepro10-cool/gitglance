<div align="center">

# 📊 gitglance

**Analyze any git repository at a glance — right in your terminal.**

Contributors · Activity · Hotspots · Stale branches

[![Python](https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-18%20passing-brightgreen)](#%EF%B8%8F-development)
[![Dependencies](https://img.shields.io/badge/dependencies-0-success)](pyproject.toml)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-lightgrey)](#-installation)

</div>

---

## ✨ Why

`git log` tells you everything and shows you nothing.
`gitglance` turns your repository's history into a few crisp, colorful terminal reports:

| Command | What you get |
|---|---|
| [`summary`](#-summary) | Commits, authors, branch, HEAD + language breakdown |
| [`authors`](#-authors) | Contributor leaderboard with +/− line stats |
| [`activity`](#-activity) | Commits per week (bars + heatmap) or per weekday |
| [`hotspots`](#-hotspots) | The files your team touches most — a.k.a. future bugs |
| [`stale`](#-stale) | Branches nobody has touched in weeks |

**Zero runtime dependencies.** Just Python ≥ 3.9 and `git` — that's it.

---

## 🚀 Installation

### Windows (one click)

Double-click **[`start.bat`](start.bat)** — it creates a virtual environment,
installs gitglance and runs it. Done.

### All platforms

```bash
pip install .
```

<details>
<summary><b>Development setup</b></summary>

```bash
git clone https://github.com/kevindepro10-cool/gitglance.git
cd gitglance
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

</details>

---

## 🕹️ Usage

```bash
gitglance summary                  # overview of the repo you are in
gitglance authors -n 5             # top 5 contributors
gitglance activity -w 26           # last 26 weeks of commit activity
gitglance activity --by-weekday    # when does your team actually commit?
gitglance hotspots -n 15           # 15 most-changed files
gitglance stale -d 60              # branches untouched for 60+ days
gitglance -C ~/src/myproject summary   # analyze any repo from anywhere
```

Use `--no-color` (or set `NO_COLOR`) to disable ANSI colors.
Full command reference: [docs/USAGE.md](docs/USAGE.md).

---

## 🖥️ Example output

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

<details>
<summary><b>More examples</b></summary>

**Authors**

```
gitglance · top authors

  Author                    Commits         +         -  Last commit
  Alice                           142    +9,812     -1,204  today        ██████████
  Bob                              51    +2,340       -512  3d ago       ████
  Carol                            21      +876       -98   12d ago      ██
```

**Stale branches**

```
gitglance · stale branches (>30 days)

     214d  feature/experiment  9f2e11aa
      87d  refactor/parser     1c3d77b2
      41d  docs/api            55ab90e1
```

</details>

---

## 📁 Project structure

```
gitglance/
├── start.bat              # Windows one-click launcher
├── src/gitglance/
│   ├── cli.py             # argument parsing + command handlers
│   ├── git.py             # safe wrappers around the git CLI
│   ├── analyze.py         # analysis logic (stats, buckets, rankings)
│   └── render.py          # ANSI colors, bars, tables
├── tests/                 # pytest suite with temp-repo fixtures
├── docs/
│   ├── USAGE.md           # full command reference
│   └── CONTRIBUTING.md    # how to contribute
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## 🛠️ Development

```bash
pip install -e ".[dev]"
pytest
```

Contributions welcome! Read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) first.

---

## 📄 License

[MIT](LICENSE) © gitglance contributors
