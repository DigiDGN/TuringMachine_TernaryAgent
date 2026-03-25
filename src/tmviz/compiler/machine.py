"""Compile high-level ternary agents into flat TM mappings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from tmviz.domain.exceptions import SpecValidationError
from tmviz.factory.validators import normalize_spec
from tmviz.model import AgentSpec

from .rules import compile_rules
from .states import compile_accept_states, compile_reject_states, compile_start_state, expand_states


@dataclass(frozen=True, slots=True)
class CompiledMachine:
    """A compiled flat TM machine ready for the existing factory."""

    name: str
    blank_symbol: str
    states: tuple[str, ...]
    start_state: str
    accept_states: tuple[str, ...]
    reject_states: tuple[str, ...]
    alphabet: tuple[str, ...]
    initial_tape: tuple[str, ...]
    initial_head: int
    rules: tuple[tuple[str, str, str, str, str], ...]
    missing_rule_policy: str

    def to_mapping(self) -> dict[str, Any]:
        """Return the compiled machine in raw TM JSON-compatible form."""

        return {
            "name": self.name,
            "blank_symbol": self.blank_symbol,
            "states": list(self.states),
            "start_state": self.start_state,
            "accept_states": list(self.accept_states),
            "reject_states": list(self.reject_states),
            "alphabet": list(self.alphabet),
            "initial_tape": list(self.initial_tape),
            "initial_head": self.initial_head,
            "rules": [list(rule) for rule in self.rules],
            "missing_rule_policy": self.missing_rule_policy,
        }


def compile_agent_spec(spec: AgentSpec) -> CompiledMachine:
    """Compile a validated AgentSpec into a flat TM machine."""

    compiled = CompiledMachine(
        name=spec.name,
        blank_symbol=spec.blank_symbol,
        states=expand_states(spec),
        start_state=compile_start_state(spec),
        accept_states=compile_accept_states(spec),
        reject_states=compile_reject_states(spec),
        alphabet=tuple(spec.alphabet),
        initial_tape=tuple(spec.initial_tape),
        initial_head=spec.initial_head,
        rules=compile_rules(spec),
        missing_rule_policy=spec.missing_rule_policy,
    )
    normalize_spec(compiled.to_mapping())
    return compiled


def compile_agent_mapping(raw: Mapping[str, Any]) -> CompiledMachine:
    """Parse and compile a raw AgentSpec-like mapping."""

    try:
        spec = AgentSpec.model_validate(raw)
    except ValidationError as exc:
        raise SpecValidationError(str(exc)) from exc
    return compile_agent_spec(spec)


def is_agent_spec_mapping(raw: Mapping[str, Any]) -> bool:
    """Return whether a mapping looks like a high-level agent spec."""

    required_keys = {"offices", "paths", "start_office"}
    return required_keys.issubset(raw)
