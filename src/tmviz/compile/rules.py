from __future__ import annotations

from typing import List, Tuple

from tmviz.model.agent_spec import AgentSpec
from tmviz.model.offices import OfficeSpec
from tmviz.model.enums import MoveIntent, IntegrityMode, OfficeRole


MOVE_INTENT_TO_TM = {
    MoveIntent.PREV: "L",
    MoveIntent.STAY: "S",
    MoveIntent.NEXT: "R",
}


def compile_office_symbol_case(
    office: OfficeSpec,
    integrity: IntegrityMode,
    symbol: str,
) -> Tuple[str, str, str]:
    # returns (write_symbol, next_office_id, move_direction)
    if office.role is OfficeRole.GENERATOR:
        if symbol == "-1":
            return "0", "arbiter", "R"
        if symbol == "0":
            return "+1", "arbiter", "R"
        if symbol == "+1":
            return "+1", "generator", "R"
        return "0", "generator", "R"

    if office.role is OfficeRole.CRITIC:
        if symbol == "-1":
            return "-1", "critic", "L"
        if symbol == "0":
            return "0", "arbiter", "S"
        if symbol == "+1":
            return "0", "arbiter", "L"
        return "_", "arbiter", "S"

    # Arbiter default law
    if symbol == "-1":
        next_off = "critic" if integrity is IntegrityMode.DEATH else "arbiter"
        return "0", next_off, "S"
    if symbol == "0":
        next_off = "generator" if integrity is IntegrityMode.SEED else "arbiter"
        return "0", next_off, "S"
    if symbol == "+1":
        return "+1", "arbiter", "R"
    return "_", ("generator" if integrity is IntegrityMode.SEED else "arbiter"), "S"


def next_integrity(
    current: IntegrityMode,
    office: OfficeRole,
    read_symbol: str,
    write_symbol: str,
) -> IntegrityMode:
    if current is IntegrityMode.DEATH and write_symbol == "-1":
        return IntegrityMode.DEATH

    if write_symbol == "0":
        return IntegrityMode.SEED

    if write_symbol == "+1":
        return IntegrityMode.LIFE

    return current


def compile_rules(spec: AgentSpec) -> List[List[str]]:
    offices_by_id = {office.id: office for office in spec.offices}
    symbols = [s for s in spec.alphabet]

    rows: List[List[str]] = []

    # build legal edge set
    legal_edges = {(p.source, p.target) for p in spec.paths if p.legal}

    for office in spec.offices:
        for integrity in IntegrityMode:
            current_state = f"{office.id}__{integrity.value}"

            for symbol in symbols:
                write_symbol, next_office_id, move = compile_office_symbol_case(
                    office=office,
                    integrity=integrity,
                    symbol=symbol,
                )

                next_mode = next_integrity(
                    current=integrity,
                    office=office.role,
                    read_symbol=symbol,
                    write_symbol=write_symbol,
                )

                next_state = f"{next_office_id}__{next_mode.value}"

                # ensure move is converted if it's a MoveIntent string
                move_dir = move
                if isinstance(move, MoveIntent):
                    move_dir = MOVE_INTENT_TO_TM[move]

                # enforce handoff legality: if next office differs, must be legal path
                if next_office_id != office.id:
                    if (office.id, next_office_id) not in legal_edges:
                        raise ValueError(
                            f"illegal office handoff: {office.id} -> {next_office_id}"
                        )

                rows.append([
                    current_state,
                    symbol,
                    next_state,
                    write_symbol,
                    move_dir,
                ])

    return rows
