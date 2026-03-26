"""Tests for SQLModel persistence layer."""

from tmviz.storage.engine import get_engine, init_db, reset_engine
from tmviz.storage.models import RunRecord, SnapshotRecord
from tmviz.storage.runs import RunStore
from tmviz.trace.snapshot import MachineSnapshot


def _fake_snapshot(step: int) -> MachineSnapshot:
    return MachineSnapshot(
        step_count=step,
        current_state=f"generator__seed",
        head_position=step,
        read_symbol="0",
        write_symbol="+1",
        move_direction="R",
        next_state="arbiter__life",
        tape_window=((step, "0"), (step + 1, "_")),
        timestamp_utc="2026-03-25T00:00:00+00:00",
    )


def test_create_run_and_list():
    store = RunStore(db_path=":memory:")
    run_id = store.create_run(
        name="test_run",
        spec_name="minimal",
        start_state="generator__seed",
        start_integrity="seed",
        alphabet=["-1", "0", "+1", "_"],
    )
    assert run_id == 1

    runs = store.list_runs()
    assert len(runs) == 1
    assert runs[0].name == "test_run"
    assert runs[0].spec_name == "minimal"


def test_record_and_retrieve_snapshots():
    store = RunStore(db_path=":memory:")
    run_id = store.create_run(
        name="snap_test",
        spec_name="minimal",
        start_state="generator__seed",
        start_integrity="seed",
        alphabet=["-1", "0", "+1", "_"],
    )

    for i in range(5):
        store.record_snapshot(run_id, _fake_snapshot(i))

    assert store.snapshot_count(run_id) == 5

    snapshots = store.get_snapshots(run_id)
    assert len(snapshots) == 5
    assert snapshots[0].step_count == 0
    assert snapshots[4].step_count == 4


def test_finish_run():
    store = RunStore(db_path=":memory:")
    run_id = store.create_run(
        name="finish_test",
        spec_name="minimal",
        start_state="generator__seed",
        start_integrity="seed",
        alphabet=["-1", "0", "+1", "_"],
    )
    store.finish_run(run_id, total_steps=42, halted=True, halt_reason="no_rule")

    record = store.get_run(run_id)
    assert record is not None
    assert record.total_steps == 42
    assert record.halted is True
    assert record.halt_reason == "no_rule"
    assert record.finished_at is not None


def test_to_machine_snapshot_roundtrip():
    store = RunStore(db_path=":memory:")
    run_id = store.create_run(
        name="roundtrip",
        spec_name="minimal",
        start_state="generator__seed",
        start_integrity="seed",
        alphabet=["-1", "0", "+1", "_"],
    )

    original = _fake_snapshot(7)
    store.record_snapshot(run_id, original)

    records = store.get_snapshots(run_id)
    restored = store.to_machine_snapshot(records[0])

    assert restored.step_count == original.step_count
    assert restored.current_state == original.current_state
    assert restored.head_position == original.head_position
    assert restored.read_symbol == original.read_symbol
    assert restored.write_symbol == original.write_symbol
    assert restored.tape_window == original.tape_window


def test_get_snapshots_with_offset_and_limit():
    store = RunStore(db_path=":memory:")
    run_id = store.create_run(
        name="paging",
        spec_name="minimal",
        start_state="generator__seed",
        start_integrity="seed",
        alphabet=["-1", "0", "+1", "_"],
    )
    for i in range(20):
        store.record_snapshot(run_id, _fake_snapshot(i))

    page = store.get_snapshots(run_id, offset=5, limit=3)
    assert len(page) == 3
    assert page[0].step_count == 5
    assert page[2].step_count == 7


def test_multiple_runs_listed_newest_first():
    store = RunStore(db_path=":memory:")
    id1 = store.create_run(
        name="first",
        spec_name="a",
        start_state="s",
        start_integrity="seed",
        alphabet=["_"],
    )
    id2 = store.create_run(
        name="second",
        spec_name="b",
        start_state="s",
        start_integrity="seed",
        alphabet=["_"],
    )
    runs = store.list_runs()
    assert len(runs) == 2
    # newest first
    assert runs[0].name == "second"
    assert runs[1].name == "first"
