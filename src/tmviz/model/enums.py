"""High-level ternary agent enums."""

from __future__ import annotations

from enum import IntEnum, StrEnum


class TernaryValue(IntEnum):
    """Tri-valued local field values."""

    NEG = -1
    ZERO = 0
    POS = 1


class IntegrityMode(StrEnum):
    """Health modes for an office."""

    DEATH = "death"
    SEED = "seed"
    LIFE = "life"


class PillarBias(StrEnum):
    """Policy bias for an office."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class OfficeRole(StrEnum):
    """Minimal office roles supported in Phase 1."""

    GENERATOR = "generator"
    ARBITER = "arbiter"
    CRITIC = "critic"


class PatchKind(StrEnum):
    """Kinds of local field patches."""

    CLAIM = "claim"
    EVIDENCE = "evidence"
    QUESTION = "question"
    TASK = "task"
    DECISION = "decision"
    MEMORY_LINK = "memory_link"
    TOOL_RESULT = "tool_result"
    RISK_MARKER = "risk_marker"
    CONSTRAINT = "constraint"


class MoveIntent(StrEnum):
    """High-level directional intent before TM flattening."""

    PREV = "prev"
    STAY = "stay"
    NEXT = "next"


INTEGRITY_RANK = {
    IntegrityMode.DEATH: 0,
    IntegrityMode.SEED: 1,
    IntegrityMode.LIFE: 2,
}

