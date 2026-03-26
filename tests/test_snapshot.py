"""Tests for MachineSnapshot capture and serialization."""

import json

from tmviz.domain.configuration import MachineConfiguration
from tmviz.domain.machine import TuringMachine
from tmviz.domain.rule import Rule
from tmviz.domain.moves import Direction
from tmviz.domain.tape import Tape
from tmviz.trace.snapshot import MachineSnapshot, capture


def _make_machine() -> TuringMachine:
    config = MachineConfiguration(
        name="snapshot_test",
        blank_symbol="_",
        states=("q0", "q1", "halt"),
        alphabet=("1", "_"),
        start_state="q0",
        accept_states=("halt",),
        reject_states=(),
        initial_tape=("1", "1", "1", "_"),
        initial_head=0,
    )
    tape = Tape.from_symbols(list(config.initial_tape), config.blank_symbol)
    rules = {
        ("q0", "1"): Rule("q0", "1", "q1", "1", Direction.RIGHT),
        ("q1", "1"): Rule("q1", "1", "q0", "1", Direction.RIGHT),
        ("q0", "_"): Rule("q0", "_", "halt", "_", Direction.STAY),
        ("q1", "_"): Rule("q1", "_", "halt", "_", Direction.STAY),
    }
    return TuringMachine(config=config, tape=tape, rules=rules)


def test_capture_produces_correct_fields():
    machine = _make_machine()
    rule = Rule("q0", "1", "q1", "1", Direction.RIGHT)
    snap = capture(machine, rule=rule)

    assert snap.step_count == 0
    assert snap.current_state == "q0"
    assert snap.head_position == 0
    assert snap.read_symbol == "1"
    assert snap.write_symbol == "1"
    assert snap.move_direction == "R"
    assert snap.next_state == "q1"
    assert len(snap.tape_window) > 0
    assert snap.timestamp_utc.endswith("+00:00")


def test_capture_without_rule():
    machine = _make_machine()
    snap = capture(machine)

    assert snap.write_symbol is None
    assert snap.move_direction is None
    assert snap.next_state is None


def test_to_dict_from_dict_roundtrip():
    machine = _make_machine()
    rule = Rule("q0", "1", "q1", "1", Direction.RIGHT)
    original = capture(machine, rule=rule)

    d = original.to_dict()
    restored = MachineSnapshot.from_dict(d)

    assert restored.step_count == original.step_count
    assert restored.current_state == original.current_state
    assert restored.head_position == original.head_position
    assert restored.read_symbol == original.read_symbol
    assert restored.write_symbol == original.write_symbol
    assert restored.move_direction == original.move_direction
    assert restored.next_state == original.next_state
    assert restored.tape_window == original.tape_window
    assert restored.timestamp_utc == original.timestamp_utc


def test_to_dict_is_json_serializable():
    machine = _make_machine()
    snap = capture(machine)
    d = snap.to_dict()
    # must not raise
    serialized = json.dumps(d)
    assert isinstance(serialized, str)
