"""Shared pytest fixtures: build small throwaway git repositories."""

from __future__ import annotations

import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def git(cwd: Path, *args: str, date: str | None = None,
        name: str = "Alice", email: str = "alice@example.com") -> str:
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin",
        "GIT_AUTHOR_NAME": name,
        "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": name,
        "GIT_COMMITTER_EMAIL": email,
        "GIT_AUTHOR_DATE": date or "",
        "GIT_COMMITTER_DATE": date or "",
    }
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True, env=env
    )
    return result.stdout


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "sample"
    repo.mkdir()
    now = datetime.now(timezone.utc)
    d_main_1 = iso(now - timedelta(days=10))
    d_main_2 = iso(now - timedelta(days=5))
    d_feature = iso(now - timedelta(days=200))

    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "Alice")
    git(repo, "config", "user.email", "alice@example.com")

    (repo / "app.py").write_text("print('hello')\n")
    (repo / "README.md").write_text("# sample\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "initial commit", date=d_main_1)

    (repo / "app.py").write_text("print('hello world')\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "update app", date=d_main_2,
        name="Bob", email="bob@example.com")

    git(repo, "checkout", "-q", "-b", "feature/old")
    (repo / "feature.txt").write_text("wip\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "wip on feature", date=d_feature)
    git(repo, "checkout", "-q", "main")
    return repo
