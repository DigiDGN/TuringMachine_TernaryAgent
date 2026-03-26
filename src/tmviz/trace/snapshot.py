"""Point-in-time machine state capture."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from tmviz.domain.machine import TuringMachine
    from tmviz.domain.rule import Rule


@dataclass(frozen=True, slots=True)
class MachineSnapshot:
    """Immutable snapshot of the machine at one step boundary."""

    step_count: int
    current_state: str
    head_position: int
    read_symbol: str
    write_symbol: str | None
    move_direction: str | None
    next_state: str | None
    tape_window: tuple[tuple[int, str], ...]
    timestamp_utc: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict suitable for JSON encoding."""

        return {
            "step_count": self.step_count,
            "current_state": self.current_state,
            "head_position": self.head_position,
            "read_symbol": self.read_symbol,
            "write_symbol": self.write_symbol,
            "move_direction": self.move_direction,
            "next_state": self.next_state,
            "tape_window": [list(cell) for cell in self.tape_window],
            "timestamp_utc": self.timestamp_utc,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MachineSnapshot:
        """Reconstruct a snapshot from a dict (inverse of :meth:`to_dict`)."""

        return cls(
            step_count=data["step_count"],
            current_state=data["current_state"],
            head_position=data["head_position"],
            read_symbol=data["read_symbol"],
            write_symbol=data.get("write_symbol"),
            move_direction=data.get("move_direction"),
            next_state=data.get("next_state"),
            tape_window=tuple(tuple(cell) for cell in data["tape_window"]),
            timestamp_utc=data["timestamp_utc"],
        )


def capture(
    machine: TuringMachine,
    rule: Rule | None = None,
    *,
    window_radius: int = 6,
) -> MachineSnapshot:
    """Capture the current machine state as an immutable snapshot.

    Parameters
    ----------
    machine:
        The running :class:`TuringMachine` instance.
    rule:
        The rule that was just applied (if any).
    window_radius:
        Number of tape cells to include on each side of the head.
    """

    return MachineSnapshot(
        step_count=machine.step_count,
        current_state=machine.current_state,
        head_position=machine.head_position,
        read_symbol=machine.read_symbol(),
        write_symbol=rule.write_symbol if rule else None,
        move_direction=rule.move_direction.value if rule else None,
        next_state=rule.next_state if rule else None,
        tape_window=tuple(machine.preview_window(radius=window_radius)),
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )
