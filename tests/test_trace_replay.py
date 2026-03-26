"""Tests for NDJSON TraceWriter and TraceReader."""

from pathlib import Path

from tmviz.trace.snapshot import MachineSnapshot
from tmviz.trace.replay import TraceWriter, TraceReader


def _fake_snapshot(step: int) -> MachineSnapshot:
    return MachineSnapshot(
        step_count=step,
        current_state=f"state_{step}",
        head_position=step,
        read_symbol="0",
        write_symbol="+1",
        move_direction="R",
        next_state=f"state_{step + 1}",
        tape_window=((step, "0"), (step + 1, "_")),
        timestamp_utc="2026-03-25T00:00:00+00:00",
    )


def test_write_and_read_roundtrip(tmp_path: Path):
    trace_file = tmp_path / "test.ndjson"

    with TraceWriter(trace_file) as writer:
        for i in range(5):
            writer.write(_fake_snapshot(i))

    reader = TraceReader(trace_file)
    assert len(reader) == 5

    snapshots = list(reader)
    assert len(snapshots) == 5
    for i, snap in enumerate(snapshots):
        assert snap.step_count == i
        assert snap.current_state == f"state_{i}"
        assert snap.head_position == i


def test_reader_random_access(tmp_path: Path):
    trace_file = tmp_path / "access.ndjson"

    with TraceWriter(trace_file) as writer:
        for i in range(10):
            writer.write(_fake_snapshot(i))

    reader = TraceReader(trace_file)
    assert reader[0].step_count == 0
    assert reader[4].step_count == 4
    assert reader[9].step_count == 9


def test_ndjson_format_one_json_per_line(tmp_path: Path):
    trace_file = tmp_path / "format.ndjson"

    with TraceWriter(trace_file) as writer:
        for i in range(3):
            writer.write(_fake_snapshot(i))

    raw_lines = trace_file.read_bytes().split(b"\n")
    non_empty = [ln for ln in raw_lines if ln.strip()]
    assert len(non_empty) == 3


def test_empty_trace_file(tmp_path: Path):
    trace_file = tmp_path / "empty.ndjson"
    trace_file.write_bytes(b"")

    reader = TraceReader(trace_file)
    assert len(reader) == 0
    assert list(reader) == []


def test_writer_creates_parent_dirs(tmp_path: Path):
    trace_file = tmp_path / "deep" / "nested" / "trace.ndjson"

    with TraceWriter(trace_file) as writer:
        writer.write(_fake_snapshot(0))

    assert trace_file.exists()
    reader = TraceReader(trace_file)
    assert len(reader) == 1
