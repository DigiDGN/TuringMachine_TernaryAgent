from __future__ import annotations

from typing import List

from dataclasses import dataclass

from tmviz.model.agent_spec import AgentSpec
from tmviz.model.enums import IntegrityMode


def expand_states(spec: AgentSpec) -> List[str]:
    states: List[str] = []
    for office in spec.offices:
        for integrity in IntegrityMode:
            states.append(f"{office.id}__{integrity.value}")
    return states


def compile_start_state(spec: AgentSpec) -> str:
    return f"{spec.start_office}__{spec.start_integrity.value}"


def compile_accept_states(spec: AgentSpec) -> List[str]:
    out: List[str] = []
    for office_id in spec.accept_offices:
        for integrity in IntegrityMode:
            out.append(f"{office_id}__{integrity.value}")
    return out


def compile_reject_states(spec: AgentSpec) -> List[str]:
    out: List[str] = []
    for office_id in spec.reject_offices:
        for integrity in IntegrityMode:
            out.append(f"{office_id}__{integrity.value}")
    return out
