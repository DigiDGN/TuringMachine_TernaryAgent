import json
from pathlib import Path

import pytest

from tmviz.compiler import compile_agent_mapping
from tmviz.domain.exceptions import SpecValidationError
from tmviz.factory.machine_factory import MachineSpecFactory


def load_example_agent_raw() -> dict[str, object]:
    path = Path(__file__).resolve().parents[1] / "examples" / "minimal_three_office.agent.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_example_compiled_snapshot() -> dict[str, object]:
    path = Path(__file__).resolve().parents[1] / "examples" / "minimal_three_office.compiled.json"
    return json.loads(path.read_text(encoding="utf-8"))


def find_rule_row(
    compiled_mapping: dict[str, object], current_state: str, read_symbol: str
) -> list[str]:
    for row in compiled_mapping["rules"]:
        if row[0] == current_state and row[1] == read_symbol:
            return row
    raise AssertionError(f"Missing rule for ({current_state}, {read_symbol})")


def test_compiler_matches_checked_in_snapshot() -> None:
    compiled = compile_agent_mapping(load_example_agent_raw()).to_mapping()

    assert compiled == load_example_compiled_snapshot()
    assert find_rule_row(compiled, "generator__seed", "0") == [
        "generator__seed",
        "0",
        "arbiter__life",
        "+1",
        "R",
    ]
    assert find_rule_row(compiled, "generator__seed", "-1") == [
        "generator__seed",
        "-1",
        "arbiter__seed",
        "0",
        "R",
    ]
    assert find_rule_row(compiled, "critic__life", "+1") == [
        "critic__life",
        "+1",
        "arbiter__seed",
        "0",
        "L",
    ]
    assert find_rule_row(compiled, "arbiter__seed", "0") == [
        "arbiter__seed",
        "0",
        "generator__seed",
        "0",
        "S",
    ]


def test_compiler_emits_unique_states_and_deterministic_rules() -> None:
    compiled = compile_agent_mapping(load_example_agent_raw())
    states = compiled.states
    rules = compiled.rules

    assert len(states) == len(set(states))
    assert compiled.start_state in states
    assert set(compiled.accept_states).issubset(states)
    assert set(compiled.reject_states).issubset(states)
    assert {row[4] for row in rules} == {"L", "R", "S"}
    assert len(rules) == len({(row[0], row[1]) for row in rules})
    assert {row[0] for row in rules}.issubset(states)
    assert {row[2] for row in rules}.issubset(states)
    assert {row[1] for row in rules}.issubset(compiled.alphabet)
    assert {row[3] for row in rules}.issubset(compiled.alphabet)


def test_compiler_respects_path_preferred_move() -> None:
    raw = load_example_agent_raw()
    raw["paths"][0]["preferred_move"] = "prev"

    compiled = compile_agent_mapping(raw).to_mapping()

    assert find_rule_row(compiled, "generator__seed", "0")[4] == "L"


def test_compiler_rejects_illegal_handoff() -> None:
    raw = load_example_agent_raw()
    raw["paths"] = [path for path in raw["paths"] if path["source"] != "generator"]

    with pytest.raises(SpecValidationError, match="illegal office handoff: generator -> arbiter"):
        compile_agent_mapping(raw)


def test_compiler_rejects_integrity_blocked_handoff() -> None:
    raw = load_example_agent_raw()
    raw["paths"][0]["min_integrity"] = "life"

    with pytest.raises(SpecValidationError, match="generator -> arbiter"):
        compile_agent_mapping(raw)


def test_terminal_offices_do_not_emit_outbound_rules() -> None:
    raw = load_example_agent_raw()
    raw["accept_offices"] = ["critic"]

    compiled = compile_agent_mapping(raw)

    assert compiled.accept_states == (
        "critic__death",
        "critic__seed",
        "critic__life",
    )
    assert all(not row[0].startswith("critic__") for row in compiled.rules)


def test_compiled_machine_runs_through_existing_factory_and_runtime() -> None:
    compiled = compile_agent_mapping(load_example_agent_raw())
    machine = MachineSpecFactory().from_mapping(compiled.to_mapping())

    history: list[tuple[str, int, list[str]]] = []
    for _ in range(6):
        result = machine.step()
        history.append(
            (
                result.current_state,
                machine.head_position,
                [machine.tape.read(index) for index in range(4)],
            )
        )

    assert history == [
        ("arbiter__life", 1, ["+1", "-1", "+1", "_"]),
        ("arbiter__seed", 1, ["+1", "0", "+1", "_"]),
        ("generator__seed", 1, ["+1", "0", "+1", "_"]),
        ("arbiter__life", 2, ["+1", "+1", "+1", "_"]),
        ("arbiter__life", 3, ["+1", "+1", "+1", "_"]),
        ("arbiter__life", 3, ["+1", "+1", "+1", "_"]),
    ]
