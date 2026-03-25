"""Compile high-level ternary agents into flat TM mappings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
import logging

from pydantic import ValidationError

from tmviz.domain.exceptions import SpecValidationError
from tmviz.factory.validators import normalize_spec
from tmviz.model import AgentSpec

from .rules import compile_rules
from .states import compile_accept_states, compile_reject_states, compile_start_state, expand_states

from tmviz.graph import build_office_graph, get_highways

# optional integrations: blinker signals and structlog logging
try:
    import blinker as _blinker  # type: ignore

    def _signal(name: str):
        return _blinker.signal(name)

except Exception:
    class _DummySignal:
        def send(self, *_, **__):
            return None

    def _signal(name: str):
        return _DummySignal()

try:
    import structlog  # type: ignore

    _LOGGER = structlog.get_logger(__name__)
except Exception:
    _LOGGER = logging.getLogger(__name__)

# define signals
compile_started = _signal("tmviz.compile.started")
compile_highways = _signal("tmviz.compile.highways")
compile_finished = _signal("tmviz.compile.finished")


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
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_mapping(self, include_metadata: bool = True) -> dict[str, Any]:
        """Return the compiled machine in raw TM JSON-compatible form.

        By default `metadata` is omitted for backward compatibility. Set
        `include_metadata=True` to attach compile-time metadata such as
        computed `highways`.
        """

        base = {
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

        if include_metadata and self.metadata:
            base["metadata"] = dict(self.metadata)

        return base


def compile_agent_spec(spec: AgentSpec) -> CompiledMachine:
    """Compile a validated AgentSpec into a flat TM machine."""

    _LOGGER.info("compile.start", name=spec.name)
    compile_started.send(name=spec.name, spec=spec)

    # compute graph-level metadata (highways) and emit a trace
    try:
        graph = build_office_graph(spec)
        highways = get_highways(graph)
        compile_highways.send(name=spec.name, highways=highways)
        _LOGGER.debug("compile.highways", name=spec.name, highways=highways)
    except Exception as exc:  # metadata computation shouldn't block compilation
        highways = []
        _LOGGER.debug("compile.highways_failed", error=str(exc))

    highways_meta = {"highways": [{"source": u, "target": v, **attrs} for u, v, attrs in highways]}

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
        metadata=highways_meta,
    )

    # validate normalized spec using factory helper (ignores extra metadata)
    normalize_spec(compiled.to_mapping())

    compile_finished.send(name=spec.name, mapping=compiled.to_mapping())
    _LOGGER.info("compile.finished", name=spec.name)
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
