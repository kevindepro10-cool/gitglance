from __future__ import annotations

from pathlib import Path

from gitglance import cli


def run_cli(*args: str, repo: Path) -> int:
    return cli.main(["-C", str(repo), "--no-color", *args])


def test_summary_exits_zero(sample_repo: Path, capsys) -> None:
    assert run_cli("summary", repo=sample_repo) == 0
    out = capsys.readouterr().out
    assert "repository summary" in out
    assert "Commits:" in out
    assert "update app" in out


def test_authors_lists_contributors(sample_repo: Path, capsys) -> None:
    assert run_cli("authors", repo=sample_repo) == 0
    out = capsys.readouterr().out
    assert "Alice" in out
    assert "Bob" in out


def test_activity_outputs_weeks(sample_repo: Path, capsys) -> None:
    assert run_cli("activity", "--weeks", "4", repo=sample_repo) == 0
    out = capsys.readouterr().out
    assert "commits per week" in out
    assert "Mon" not in out


def test_activity_by_weekday(sample_repo: Path, capsys) -> None:
    assert run_cli("activity", "--by-weekday", repo=sample_repo) == 0
    out = capsys.readouterr().out
    assert "Mon" in out
    assert "Sun" in out


def test_hotspots_output(sample_repo: Path, capsys) -> None:
    assert run_cli("hotspots", repo=sample_repo) == 0
    out = capsys.readouterr().out
    assert "app.py" in out


def test_stale_reports_old_branch(sample_repo: Path, capsys) -> None:
    assert run_cli("stale", "--days", "30", repo=sample_repo) == 0
    out = capsys.readouterr().out
    assert "feature/old" in out


def test_non_repo_path_fails(tmp_path: Path, capsys) -> None:
    assert cli.main(["-C", str(tmp_path), "summary"]) == 2
    assert "not a git repository" in capsys.readouterr().err


def test_version_flag(capsys) -> None:
    try:
        cli.main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    assert "gitglance" in capsys.readouterr().out
