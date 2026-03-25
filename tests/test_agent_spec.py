import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tmviz.model import AgentSpec


def load_example_agent_raw() -> dict[str, object]:
    path = Path(__file__).resolve().parents[1] / "examples" / "minimal_three_office.agent.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_agent_spec_accepts_canonical_example() -> None:
    spec = AgentSpec.model_validate(load_example_agent_raw())

    assert spec.start_office == "generator"
    assert spec.start_integrity.value == "seed"
    assert spec.symbol_at_head() == "0"


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (
            lambda raw: raw["offices"][0].__setitem__("role", "oracle"),
            "Input should be 'generator', 'arbiter' or 'critic'",
        ),
        (
            lambda raw: raw["field_seed"].append(
                {"id": "c1", "kind": "claim", "confidence": 1.5}
            ),
            "Input should be less than or equal to 1",
        ),
    ],
)
def test_agent_spec_rejects_invalid_enums_and_ranges(
    mutator: callable, message: str
) -> None:
    raw = load_example_agent_raw()
    mutator(raw)

    with pytest.raises(ValidationError, match=message):
        AgentSpec.model_validate(raw)


def test_agent_spec_rejects_duplicate_office_ids() -> None:
    raw = load_example_agent_raw()
    raw["offices"][1]["id"] = raw["offices"][0]["id"]

    with pytest.raises(ValidationError, match="office ids must be unique"):
        AgentSpec.model_validate(raw)


def test_agent_spec_rejects_duplicate_roles() -> None:
    raw = load_example_agent_raw()
    raw["offices"][1]["role"] = "generator"

    with pytest.raises(
        ValidationError,
        match="exactly one generator, one arbiter, and one critic office",
    ):
        AgentSpec.model_validate(raw)


def test_agent_spec_rejects_missing_path_endpoint() -> None:
    raw = load_example_agent_raw()
    raw["paths"][0]["target"] = "ghost"

    with pytest.raises(
        ValidationError,
        match="every path endpoint must reference a defined office",
    ):
        AgentSpec.model_validate(raw)


def test_agent_spec_rejects_unknown_start_office() -> None:
    raw = load_example_agent_raw()
    raw["start_office"] = "ghost"

    with pytest.raises(ValidationError, match="start_office must reference a defined office"):
        AgentSpec.model_validate(raw)


def test_agent_spec_rejects_bad_start_symbol() -> None:
    raw = load_example_agent_raw()
    raw["start_symbol"] = "+1"

    with pytest.raises(
        ValidationError,
        match="start_symbol must match the symbol under the initial head",
    ):
        AgentSpec.model_validate(raw)


def test_agent_spec_rejects_tape_symbols_outside_the_alphabet() -> None:
    raw = load_example_agent_raw()
    raw["initial_tape"][2] = "x"

    with pytest.raises(ValidationError, match="initial_tape contains symbols outside the alphabet"):
        AgentSpec.model_validate(raw)
