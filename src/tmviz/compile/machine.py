from __future__ import annotations

from dataclasses import dataclass
from typing import List

from tmviz.model.agent_spec import AgentSpec
from tmviz.compile.states import (
    expand_states,
    compile_start_state,
    compile_accept_states,
    compile_reject_states,
)
from tmviz.compile.rules import compile_rules


@dataclass(frozen=True)
class CompiledRule:
    current_state: str
    read_symbol: str
    next_state: str
    write_symbol: str
    move_direction: str


@dataclass
class CompiledMachine:
    name: str
    blank_symbol: str
    states: List[str]
    start_state: str
    accept_states: List[str]
    reject_states: List[str]
    alphabet: List[str]
    initial_tape: List[str]
    initial_head: int
    rules: List[List[str]]
    missing_rule_policy: str


def compile_agent_to_machine(spec: AgentSpec) -> CompiledMachine:
    states = expand_states(spec)
    start = compile_start_state(spec)
    accept = compile_accept_states(spec)
    reject = compile_reject_states(spec)
    rules = compile_rules(spec)

    return CompiledMachine(
        name=spec.name,
        blank_symbol=spec.blank_symbol,
        states=states,
        start_state=start,
        accept_states=accept,
        reject_states=reject,
        alphabet=spec.alphabet,
        initial_tape=spec.initial_tape,
        initial_head=spec.initial_head,
        rules=rules,
        missing_rule_policy=spec.missing_rule_policy,
    )
