"""State flattening helpers."""

from __future__ import annotations

from tmviz.model import AgentSpec, IntegrityMode


def compile_state_name(office_id: str, integrity: IntegrityMode) -> str:
    """Build a flattened TM state name."""

    return f"{office_id}__{integrity.value}"


def expand_states(spec: AgentSpec) -> tuple[str, ...]:
    """Expand authored offices into flattened TM states."""

    return tuple(
        compile_state_name(office.id, integrity)
        for office in spec.offices
        for integrity in IntegrityMode
    )


def compile_start_state(spec: AgentSpec) -> str:
    """Compile the authored start office and integrity into a TM start state."""

    return compile_state_name(spec.start_office, spec.start_integrity)


def compile_accept_states(spec: AgentSpec) -> tuple[str, ...]:
    """Compile authored accept offices into flattened accept states."""

    return tuple(
        compile_state_name(office_id, integrity)
        for office_id in spec.accept_offices
        for integrity in IntegrityMode
    )


def compile_reject_states(spec: AgentSpec) -> tuple[str, ...]:
    """Compile authored reject offices into flattened reject states."""

    return tuple(
        compile_state_name(office_id, integrity)
        for office_id in spec.reject_offices
        for integrity in IntegrityMode
    )
