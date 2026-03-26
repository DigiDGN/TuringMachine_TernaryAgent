"""Tests for the Typer CLI."""

import json
from pathlib import Path

from typer.testing import CliRunner

from tmviz.cli.main import app

runner = CliRunner()


def _write_spec(tmp_path: Path) -> Path:
    """Write a minimal agent spec and return its path."""
    from conftest import MINIMAL_AGENT

    spec_path = tmp_path / "test.agent.json"
    spec_path.write_text(json.dumps(MINIMAL_AGENT), encoding="utf8")
    return spec_path


def test_compile_to_stdout(tmp_path: Path):
    spec_path = _write_spec(tmp_path)
    result = runner.invoke(app, ["compile", str(spec_path)])
    assert result.exit_code == 0
    # output should contain valid JSON with states
    assert "generator__seed" in result.stdout


def test_compile_to_file(tmp_path: Path):
    spec_path = _write_spec(tmp_path)
    out_path = tmp_path / "out.json"
    result = runner.invoke(app, ["compile", str(spec_path), str(out_path)])
    assert result.exit_code == 0
    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf8"))
    assert "states" in data
    assert "rules" in data


def test_run_persists_to_db(tmp_path: Path):
    spec_path = _write_spec(tmp_path)
    db_path = tmp_path / "test.db"
    result = runner.invoke(app, [
        "run", str(spec_path),
        "--steps", "10",
        "--db", str(db_path),
    ])
    assert result.exit_code == 0
    assert "completed" in result.stdout.lower() or "Run" in result.stdout


def test_run_with_trace(tmp_path: Path):
    spec_path = _write_spec(tmp_path)
    db_path = tmp_path / "test.db"
    trace_path = tmp_path / "trace.ndjson"
    result = runner.invoke(app, [
        "run", str(spec_path),
        "--steps", "5",
        "--db", str(db_path),
        "--trace", str(trace_path),
    ])
    assert result.exit_code == 0
    assert trace_path.exists()
    lines = [ln for ln in trace_path.read_bytes().split(b"\n") if ln.strip()]
    assert len(lines) == 5


def test_runs_list_empty(tmp_path: Path):
    db_path = tmp_path / "empty.db"
    result = runner.invoke(app, ["runs", "--db", str(db_path)])
    assert result.exit_code == 0
    assert "No runs" in result.stdout


def test_runs_list_after_run(tmp_path: Path):
    spec_path = _write_spec(tmp_path)
    db_path = tmp_path / "list.db"
    runner.invoke(app, [
        "run", str(spec_path),
        "--steps", "5",
        "--db", str(db_path),
    ])
    result = runner.invoke(app, ["runs", "--db", str(db_path)])
    assert result.exit_code == 0
    # Rich table may truncate long names with ellipsis
    assert "minimal_three" in result.stdout


def test_inspect_run(tmp_path: Path):
    spec_path = _write_spec(tmp_path)
    db_path = tmp_path / "inspect.db"
    runner.invoke(app, [
        "run", str(spec_path),
        "--steps", "5",
        "--db", str(db_path),
    ])
    result = runner.invoke(app, ["inspect", "1", "--db", str(db_path)])
    assert result.exit_code == 0
    assert "generator" in result.stdout.lower()


def test_inspect_missing_run(tmp_path: Path):
    db_path = tmp_path / "empty.db"
    result = runner.invoke(app, ["inspect", "999", "--db", str(db_path)])
    assert result.exit_code == 1
