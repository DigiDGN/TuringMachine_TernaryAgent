"""Integration test: run a compiled machine with tracing enabled."""

from pathlib import Path

from conftest import MINIMAL_AGENT
from tmviz.compiler import compile_agent_mapping
from tmviz.factory.machine_factory import MachineSpecFactory
from tmviz.trace.snapshot import capture
from tmviz.trace.replay import TraceReader, TraceWriter


def test_run_machine_with_trace_writer(tmp_path: Path):
    trace_file = tmp_path / "run.ndjson"

    compiled = compile_agent_mapping(MINIMAL_AGENT)
    factory = MachineSpecFactory()
    machine = factory.from_mapping(compiled.to_mapping())

    steps = 10
    with TraceWriter(trace_file) as writer:
        for _ in range(steps):
            if machine.halted:
                break
            rule = machine.lookup_rule()
            snap = capture(machine, rule=rule)
            writer.write(snap)
            machine.step()

    reader = TraceReader(trace_file)
    assert len(reader) == steps

    # verify monotonic step counts
    snapshots = list(reader)
    for i, snap in enumerate(snapshots):
        assert snap.step_count == i

    # verify first snapshot starts in the compiled start state
    assert snapshots[0].current_state == compiled.start_state


def test_trace_captures_tape_window(tmp_path: Path):
    trace_file = tmp_path / "tape.ndjson"

    compiled = compile_agent_mapping(MINIMAL_AGENT)
    factory = MachineSpecFactory()
    machine = factory.from_mapping(compiled.to_mapping())

    with TraceWriter(trace_file) as writer:
        snap = capture(machine, window_radius=3)
        writer.write(snap)

    reader = TraceReader(trace_file)
    snap = reader[0]
    # tape window should contain tuples of (position, symbol)
    assert len(snap.tape_window) > 0
    positions = [pos for pos, _sym in snap.tape_window]
    assert snap.head_position in positions
