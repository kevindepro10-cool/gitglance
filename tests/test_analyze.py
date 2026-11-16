from __future__ import annotations

from pathlib import Path

import pytest

from gitglance import analyze, git


def test_resolve_repo_returns_toplevel(sample_repo: Path) -> None:
    nested = sample_repo / "sub"
    nested.mkdir()
    assert git.resolve_repo(nested) == sample_repo.resolve()


def test_resolve_repo_rejects_non_repo(tmp_path: Path) -> None:
    with pytest.raises(git.GitError):
        git.resolve_repo(tmp_path)


def test_log_all_parses_commits(sample_repo: Path) -> None:
    commits = git.log_all(sample_repo)
    assert len(commits) == 3
    assert commits[0].subject == "update app"
    assert {c.author_email for c in commits} == {"alice@example.com", "bob@example.com"}


def test_author_stats_counts_commits(sample_repo: Path) -> None:
    stats = analyze.author_stats(sample_repo)
    assert len(stats) == 2
    assert stats[0].name == "Alice"
    assert stats[0].commits == 2
    bob = next(s for s in stats if s.name == "Bob")
    assert bob.commits == 1


def test_author_stats_sums_lines(sample_repo: Path) -> None:
    stats = analyze.author_stats(sample_repo)
    alice = next(s for s in stats if s.name == "Alice")
    assert alice.additions == 3


def test_activity_by_week_buckets(sample_repo: Path) -> None:
    data = analyze.activity_by_week(sample_repo, weeks=12)
    assert len(data) == 12
    total = sum(count for _, count in data)
    assert total == 2


def test_activity_by_weekday(sample_repo: Path) -> None:
    data = analyze.activity_by_weekday(sample_repo)
    assert [label for label, _ in data] == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    assert sum(count for _, count in data) == 3


def test_hotspots_ranks_files(sample_repo: Path) -> None:
    spots = analyze.hotspots(sample_repo, top=5)
    paths = [path for path, _ in spots]
    assert "app.py" in paths
    assert spots[0][1] >= spots[-1][1]


def test_stale_branches_finds_old_feature(sample_repo: Path) -> None:
    stale = analyze.stale_branches(sample_repo, days=30)
    names = [branch.name for branch, _ in stale]
    assert "feature/old" in names
    assert "main" not in names


def test_summarize_aggregates(sample_repo: Path) -> None:
    summary = analyze.summarize(sample_repo)
    assert summary.total_commits == 3
    assert summary.author_count == 2
    assert summary.branch == "main"
    assert summary.head is not None
    assert summary.head.subject == "update app"
    assert summary.tracked_files == 2
    languages = {stat.language for stat in summary.languages}
    assert "Python" in languages
    assert "Markdown" in languages
