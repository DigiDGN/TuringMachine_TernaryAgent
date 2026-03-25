"""Rule compilation for minimal ternary agents."""

from __future__ import annotations

from dataclasses import dataclass

from tmviz.domain.exceptions import SpecValidationError
from tmviz.graph import build_office_graph, resolve_handoff_move
from tmviz.model import AgentSpec, IntegrityMode, MoveIntent, OfficeRole

from .states import compile_state_name

MOVE_INTENT_TO_TM = {
    MoveIntent.PREV: "L",
    MoveIntent.STAY: "S",
    MoveIntent.NEXT: "R",
}

SUPPORTED_TERNARY_SYMBOLS = {"-1", "0", "+1"}


@dataclass(frozen=True, slots=True)
class RuleTemplate:
    """Role-level transition before office-id flattening."""

    write_symbol: str
    next_role: OfficeRole
    move_intent: MoveIntent


def compile_role_symbol_case(
    role: OfficeRole,
    integrity: IntegrityMode,
    symbol: str,
    blank_symbol: str,
) -> RuleTemplate:
    """Compile one office-role and symbol case into a role-level template."""

    if symbol not in SUPPORTED_TERNARY_SYMBOLS and symbol != blank_symbol:
        raise SpecValidationError(
            f"Phase 1 only supports symbols {sorted(SUPPORTED_TERNARY_SYMBOLS | {blank_symbol})}"
        )

    if role is OfficeRole.GENERATOR:
        if symbol == "-1":
            return RuleTemplate("0", OfficeRole.ARBITER, MoveIntent.NEXT)
        if symbol == "0":
            return RuleTemplate("+1", OfficeRole.ARBITER, MoveIntent.NEXT)
        if symbol == "+1":
            return RuleTemplate("+1", OfficeRole.GENERATOR, MoveIntent.NEXT)
        return RuleTemplate("0", OfficeRole.GENERATOR, MoveIntent.NEXT)

    if role is OfficeRole.CRITIC:
        if symbol == "-1":
            return RuleTemplate("-1", OfficeRole.CRITIC, MoveIntent.PREV)
        if symbol == "0":
            return RuleTemplate("0", OfficeRole.ARBITER, MoveIntent.STAY)
        if symbol == "+1":
            return RuleTemplate("0", OfficeRole.ARBITER, MoveIntent.PREV)
        return RuleTemplate(blank_symbol, OfficeRole.ARBITER, MoveIntent.STAY)

    if symbol == "-1":
        next_role = OfficeRole.CRITIC if integrity is IntegrityMode.DEATH else OfficeRole.ARBITER
        return RuleTemplate("0", next_role, MoveIntent.STAY)
    if symbol == "0":
        next_role = OfficeRole.GENERATOR if integrity is IntegrityMode.SEED else OfficeRole.ARBITER
        return RuleTemplate("0", next_role, MoveIntent.STAY)
    if symbol == "+1":
        return RuleTemplate("+1", OfficeRole.ARBITER, MoveIntent.NEXT)
    next_role = OfficeRole.GENERATOR if integrity is IntegrityMode.SEED else OfficeRole.ARBITER
    return RuleTemplate(blank_symbol, next_role, MoveIntent.STAY)


def next_integrity(current: IntegrityMode, write_symbol: str) -> IntegrityMode:
    """Advance integrity using the first-pass law."""

    if current is IntegrityMode.DEATH and write_symbol == "-1":
        return IntegrityMode.DEATH
    if write_symbol == "0":
        return IntegrityMode.SEED
    if write_symbol == "+1":
        return IntegrityMode.LIFE
    return current


def compile_rules(spec: AgentSpec) -> tuple[tuple[str, str, str, str, str], ...]:
    """Compile authored offices and paths into TM rule rows."""

    graph = build_office_graph(spec)
    terminal_offices = set(spec.accept_offices) | set(spec.reject_offices)
    rows: list[tuple[str, str, str, str, str]] = []

    for office in spec.offices:
        for integrity in IntegrityMode:
            if office.id in terminal_offices:
                continue
            current_state = compile_state_name(office.id, integrity)
            for symbol in spec.alphabet:
                template = compile_role_symbol_case(
                    role=office.role,
                    integrity=integrity,
                    symbol=symbol,
                    blank_symbol=spec.blank_symbol,
                )
                target_office = spec.office_by_role(template.next_role).id
                move_intent = resolve_handoff_move(
                    graph=graph,
                    source=office.id,
                    target=target_office,
                    integrity=integrity,
                )
                compiled_move = move_intent if move_intent is not None else template.move_intent
                next_state = compile_state_name(
                    target_office,
                    next_integrity(current=integrity, write_symbol=template.write_symbol),
                )
                rows.append(
                    (
                        current_state,
                        symbol,
                        next_state,
                        template.write_symbol,
                        MOVE_INTENT_TO_TM[compiled_move],
                    )
                )

    return tuple(rows)
