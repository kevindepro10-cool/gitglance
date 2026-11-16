"""Analysis logic: turn raw git data into report models."""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import git

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".tox", ".idea", ".vscode",
}

LANGUAGE_MAP = {
    ".py": "Python", ".pyw": "Python",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".java": "Java", ".kt": "Kotlin", ".swift": "Swift",
    ".c": "C", ".h": "C", ".cpp": "C++", ".cc": "C++", ".hpp": "C++",
    ".cs": "C#", ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".lua": "Lua", ".pl": "Perl", ".r": "R", ".jl": "Julia",
    ".md": "Markdown", ".rst": "reStructuredText", ".txt": "Text",
    ".json": "JSON", ".yml": "YAML", ".yaml": "YAML", ".toml": "TOML",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS", ".sql": "SQL",
    ".dart": "Dart", ".scala": "Scala", ".ex": "Elixir", ".exs": "Elixir",
    ".hs": "Haskell", ".zig": "Zig", ".vim": "Vim Script",
}


@dataclass
class AuthorStat:
    name: str
    email: str
    commits: int = 0
    additions: int = 0
    deletions: int = 0
    last_commit: datetime | None = None


@dataclass
class LanguageStat:
    language: str
    files: int = 0
    bytes: int = 0


@dataclass
class RepoSummary:
    path: Path
    branch: str
    head: git.Commit | None
    total_commits: int
    author_count: int
    first_commit: datetime | None
    last_commit: datetime | None
    languages: list[LanguageStat] = field(default_factory=list)
    tracked_files: int = 0


def author_stats(cwd: Path) -> list[AuthorStat]:
    commits = git.log_all(cwd)
    by_email: dict[str, AuthorStat] = {}
    for commit in commits:
        stat = by_email.get(commit.author_email)
        if stat is None:
            stat = AuthorStat(commit.author_name, commit.author_email)
            by_email[commit.author_email] = stat
        stat.commits += 1
        if stat.last_commit is None or commit.date > stat.last_commit:
            stat.last_commit = commit.date
        if stat.name != commit.author_name:
            stat.name = commit.author_name

    for author, added, deleted in git.numstat_all(cwd):
        stat = next((s for s in by_email.values() if s.name == author), None)
        if stat is None:
            continue
        if added != "-":
            stat.additions += int(added)
        if deleted != "-":
            stat.deletions += int(deleted)

    return sorted(by_email.values(), key=lambda s: s.commits, reverse=True)


def activity_by_week(cwd: Path, weeks: int = 12) -> list[tuple[str, int]]:
    """Return the last `weeks` ISO weeks (oldest first) with commit counts."""
    commits = git.log_all(cwd)
    today = datetime.now(timezone.utc).date()
    start_of_week = today - timedelta(days=today.weekday())
    buckets: Counter[str] = Counter()
    for offset in range(weeks):
        week_start = start_of_week - timedelta(weeks=offset)
        buckets[week_start.isoformat()] = 0
    for commit in commits:
        d = commit.date.date()
        week_start = d - timedelta(days=d.weekday())
        key = week_start.isoformat()
        if key in buckets:
            buckets[key] += 1
    return sorted(buckets.items())


def activity_by_weekday(cwd: Path) -> list[tuple[str, int]]:
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts = Counter()
    for commit in git.log_all(cwd):
        counts[commit.date.weekday()] += 1
    return [(names[i], counts.get(i, 0)) for i in range(7)]


def hotspots(cwd: Path, top: int = 10) -> list[tuple[str, int]]:
    counts = Counter(git.changed_files(cwd))
    return counts.most_common(top)


def stale_branches(cwd: Path, days: int = 30) -> list[tuple[git.Branch, int]]:
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    result = []
    for branch in git.branches(cwd):
        ts = branch.last_commit.timestamp()
        if ts < cutoff:
            result.append((branch, int((datetime.now(timezone.utc).timestamp() - ts) // 86400)))
    return sorted(result, key=lambda item: item[1], reverse=True)


def language_stats(repo: Path, top: int = 8) -> list[LanguageStat]:
    counts: dict[str, LanguageStat] = {}
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".git")]
        for file_name in files:
            ext = Path(file_name).suffix.lower()
            language = LANGUAGE_MAP.get(ext)
            if language is None:
                continue
            try:
                size = os.path.getsize(os.path.join(root, file_name))
            except OSError:
                continue
            stat = counts.setdefault(language, LanguageStat(language))
            stat.files += 1
            stat.bytes += size
    ranked = sorted(counts.values(), key=lambda s: s.bytes, reverse=True)
    return ranked[:top]


def tracked_file_count(cwd: Path) -> int:
    raw = git.run(["ls-files"], cwd)
    return sum(1 for line in raw.splitlines() if line.strip())


def summarize(cwd: Path) -> RepoSummary:
    repo = git.resolve_repo(cwd)
    commits = git.log_all(repo)
    dates = [c.date for c in commits]
    return RepoSummary(
        path=repo,
        branch=git.current_branch(repo),
        head=git.head_commit(repo),
        total_commits=git.total_commits(repo),
        author_count=len({c.author_email for c in commits}),
        first_commit=min(dates) if dates else None,
        last_commit=max(dates) if dates else None,
        languages=language_stats(repo),
        tracked_files=tracked_file_count(repo),
    )
