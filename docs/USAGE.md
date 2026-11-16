# Command reference

Global options (work before **and** after the subcommand):

| Flag | Description |
|---|---|
| `-C, --repo <path>` | Path inside the repository to analyze (default: current directory) |
| `--no-color` | Disable ANSI colors (also honors the `NO_COLOR` environment variable) |
| `--version` | Print the version and exit |

## `gitglance summary`

Repository overview: path, current branch, total commits, author count,
tracked files, first/last commit, HEAD subject and a language breakdown
with proportional bars.

```bash
gitglance summary
gitglance -C ~/src/myproject summary
```

## `gitglance authors`

Contributor leaderboard sorted by commit count, with additions and deletions
per author.

```bash
gitglance authors            # top 10
gitglance authors -n 5       # top 5
```

## `gitglance activity`

Commit activity over time.

```bash
gitglance activity               # last 12 weeks, one bar per week
gitglance activity -w 26         # last 26 weeks
gitglance activity --by-weekday  # commits per weekday (Mon–Sun)
```

The weekly view ends with a small heatmap strip summarizing the same data.

## `gitglance hotspots`

The most frequently changed files across all branches — a good proxy for
complex, bug-prone areas of the codebase.

```bash
gitglance hotspots            # top 10
gitglance hotspots -n 15      # top 15
```

## `gitglance stale`

Local branches whose last commit is older than the given threshold.
Age is shown in days; anything older than 180 days is highlighted red.

```bash
gitglance stale            # older than 30 days
gitglance stale -d 60      # older than 60 days
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `2` | Error (e.g. path is not a git repository) |
