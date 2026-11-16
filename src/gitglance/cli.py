"""Command-line interface for gitglance."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, analyze, git, render
from .render import Painter


def _add_global_flags(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("-C", "--repo", default=argparse.SUPPRESS, type=Path,
                     help="path inside the repository (default: cwd)")
    sub.add_argument("--no-color", default=argparse.SUPPRESS, action="store_true",
                     help="disable colored output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitglance",
        description="Analyze any git repository at a glance.",
    )
    parser.add_argument("--version", action="version", version=f"gitglance {__version__}")
    parser.add_argument(
        "-C", "--repo", default=".", type=Path, help="path inside the repository (default: cwd)"
    )
    parser.add_argument("--no-color", action="store_true", help="disable colored output")
    sub = parser.add_subparsers(dest="command", required=True)

    _add_global_flags(sub.add_parser("summary", help="repository overview"))

    authors = sub.add_parser("authors", help="contributor leaderboard")
    _add_global_flags(authors)
    authors.add_argument("-n", "--top", type=int, default=10, help="show top N authors")

    activity = sub.add_parser("activity", help="commit activity over time")
    _add_global_flags(activity)
    activity.add_argument("-w", "--weeks", type=int, default=12, help="number of weeks")
    activity.add_argument("--by-weekday", action="store_true", help="break down by weekday")

    hotspots = sub.add_parser("hotspots", help="most frequently changed files")
    _add_global_flags(hotspots)
    hotspots.add_argument("-n", "--top", type=int, default=10, help="show top N files")

    stale = sub.add_parser("stale", help="branches without recent commits")
    _add_global_flags(stale)
    stale.add_argument("-d", "--days", type=int, default=30, help="staleness threshold in days")

    return parser


def cmd_summary(repo: Path, paint: Painter) -> int:
    summary = analyze.summarize(repo)
    print(paint.bold(paint.cyan("gitglance")) + paint.dim(" · repository summary"))
    print()
    print(f"  {paint.dim('Path:')}      {summary.path}")
    print(f"  {paint.dim('Branch:')}    {paint.magenta(summary.branch)}")
    print(f"  {paint.dim('Commits:')}   {render.fmt_number(summary.total_commits)}")
    print(f"  {paint.dim('Authors:')}   {summary.author_count}")
    print(f"  {paint.dim('Tracked:')}   {render.fmt_number(summary.tracked_files)} files")
    print(f"  {paint.dim('First:')}     {render.fmt_date(summary.first_commit)}")
    print(f"  {paint.dim('Last:')}      {render.fmt_date(summary.last_commit)}"
          + paint.dim(f" ({render.relative_days(summary.last_commit)})"))
    if summary.head:
        print()
        print(f"  {paint.dim('HEAD:')}      {paint.yellow(summary.head.hash[:8])} {summary.head.subject}")
    if summary.languages:
        print()
        print(paint.bold("  Languages"))
        max_bytes = summary.languages[0].bytes if summary.languages else 0
        for stat in summary.languages:
            line = render.bar(paint, stat.bytes, max_bytes, width=20)
            pct = f"{stat.bytes / sum(s.bytes for s in summary.languages) * 100:4.1f}%"
            print(f"    {stat.language:<14} {line} {paint.dim(pct)}  {stat.files} files")
    return 0


def cmd_authors(repo: Path, paint: Painter, top: int) -> int:
    stats = analyze.author_stats(repo)[:top]
    if not stats:
        print(paint.dim("No commits found."))
        return 0
    print(paint.bold(paint.cyan("gitglance")) + paint.bold(" · top authors"))
    print()
    header = f"  {'Author':<24} {'Commits':>8} {'+':>9} {'-':>9}  {'Last commit':<12}"
    print(paint.dim(header))
    max_commits = stats[0].commits
    for stat in stats:
        name = stat.name if len(stat.name) <= 23 else stat.name[:22] + "…"
        bars = render.bar(paint, stat.commits, max_commits, width=10)
        print(
            f"  {name:<24} {stat.commits:>8} "
            f"{paint.green('+' + render.fmt_number(stat.additions)):>9} "
            f"{paint.red('-' + render.fmt_number(stat.deletions)):>9}  "
            f"{render.relative_days(stat.last_commit):<12} {bars}"
        )
    return 0


def cmd_activity(repo: Path, paint: Painter, weeks: int, by_weekday: bool) -> int:
    if by_weekday:
        data = analyze.activity_by_weekday(repo)
        max_value = max((count for _, count in data), default=0)
        print(paint.bold("gitglance · commits by weekday"))
        print()
        for label, count in data:
            line = render.bar(paint, count, max_value, width=30)
            print(f"  {label}  {line} {count:>5}")
        return 0

    data = analyze.activity_by_week(repo, weeks=weeks)
    max_value = max((count for _, count in data), default=0)
    print(paint.bold(f"gitglance · commits per week (last {weeks} weeks)"))
    print()
    for label, count in data:
        line = render.bar(paint, count, max_value, width=30)
        print(f"  {label}  {line} {count:>5}")
    print()
    print(paint.dim("  " + "".join(render.heatmap(paint, c, max_value) for _, c in data)))
    return 0


def cmd_hotspots(repo: Path, paint: Painter, top: int) -> int:
    spots = analyze.hotspots(repo, top=top)
    if not spots:
        print(paint.dim("No commits found."))
        return 0
    print(paint.bold("gitglance · most changed files"))
    print()
    max_count = spots[0][1]
    for path, count in spots:
        line = render.bar(paint, count, max_count, width=20)
        print(f"  {count:>5}×  {line}  {path}")
    return 0


def cmd_stale(repo: Path, paint: Painter, days: int) -> int:
    stale = analyze.stale_branches(repo, days=days)
    if not stale:
        print(paint.green(f"No branches older than {days} days. Clean house!"))
        return 0
    print(paint.bold(f"gitglance · stale branches (>{days} days)"))
    print()
    for branch, age in stale:
        age_text = paint.red(f"{age}d") if age > 180 else paint.yellow(f"{age}d")
        print(f"  {age_text:>7}  {paint.magenta(branch.name)}  {paint.dim(branch.hash[:8])}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paint = Painter(use_color=args.no_color is False)
    try:
        repo = git.resolve_repo(args.repo)
    except git.GitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    handlers = {
        "summary": lambda: cmd_summary(repo, paint),
        "authors": lambda: cmd_authors(repo, paint, args.top),
        "activity": lambda: cmd_activity(repo, paint, args.weeks, args.by_weekday),
        "hotspots": lambda: cmd_hotspots(repo, paint, args.top),
        "stale": lambda: cmd_stale(repo, paint, args.days),
    }
    try:
        return handlers[args.command]()
    except git.GitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
