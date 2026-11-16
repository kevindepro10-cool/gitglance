"""Thin, safe wrappers around the git command line."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class GitError(RuntimeError):
    """Raised when a git command fails or the path is not a repository."""


@dataclass(frozen=True)
class Commit:
    hash: str
    author_name: str
    author_email: str
    date: datetime
    subject: str


@dataclass(frozen=True)
class Branch:
    name: str
    last_commit: datetime
    hash: str


_LOG_FORMAT = "%H%x1f%an%x1f%ae%x1f%aI%x1f%s"


def run(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:  # pragma: no cover - git always present in CI
        raise GitError("git executable not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "").strip()
        raise GitError(message or f"git {' '.join(args)} failed") from exc
    return result.stdout


def resolve_repo(path: Path) -> Path:
    repo = path.resolve()
    if not repo.is_dir():
        raise GitError(f"not a directory: {repo}")
    try:
        top = run(["rev-parse", "--show-toplevel"], repo).strip()
    except GitError as exc:
        raise GitError(f"not a git repository: {repo}") from exc
    return Path(top)


def is_repo(path: Path) -> bool:
    try:
        resolve_repo(path)
        return True
    except GitError:
        return False


def parse_log(raw: str) -> list[Commit]:
    commits: list[Commit] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) != 5:
            continue
        sha, name, email, iso, subject = parts
        try:
            date = datetime.fromisoformat(iso)
        except ValueError:
            continue
        commits.append(Commit(sha, name, email, date, subject))
    return commits


def log_all(cwd: Path) -> list[Commit]:
    raw = run(["log", "--all", f"--pretty=format:{_LOG_FORMAT}"], cwd)
    return parse_log(raw)


def numstat_all(cwd: Path) -> list[tuple[str, str, str]]:
    """Return (author, additions, deletions) per changed file across all commits."""
    raw = run(
        ["log", "--all", "--numstat", "--pretty=format:%x1e%an"], cwd
    )
    rows: list[tuple[str, str, str]] = []
    author = ""
    for line in raw.split("\n"):
        if line.startswith("\x1e"):
            author = line[1:].strip()
            continue
        parts = line.split("\t")
        if len(parts) == 3 and author:
            rows.append((author, parts[0], parts[1]))
    return rows


def changed_files(cwd: Path) -> list[str]:
    raw = run(["log", "--all", "--pretty=format:", "--name-only"], cwd)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def branches(cwd: Path) -> list[Branch]:
    raw = run(
        [
            "for-each-ref",
            "refs/heads",
            "--sort=-committerdate",
            "--format=%(refname:short)%1f%(committerdate:iso8601-strict)%1f%(objectname:short)",
        ],
        cwd,
    )
    result: list[Branch] = []
    for line in raw.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        name, iso, sha = parts
        try:
            date = datetime.fromisoformat(iso)
        except ValueError:
            continue
        result.append(Branch(name, date, sha))
    return result


def current_branch(cwd: Path) -> str:
    raw = run(["rev-parse", "--abbrev-ref", "HEAD"], cwd).strip()
    return raw or "HEAD (detached)"


def head_commit(cwd: Path) -> Commit | None:
    raw = run(["log", "-1", f"--pretty=format:{_LOG_FORMAT}"], cwd)
    commits = parse_log(raw)
    return commits[0] if commits else None


def total_commits(cwd: Path) -> int:
    raw = run(["rev-list", "--all", "--count"], cwd)
    try:
        return int(raw.strip())
    except ValueError:
        return 0
