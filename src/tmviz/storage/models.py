"""SQLModel table definitions for persisted runs and snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlmodel import Field, SQLModel


class RunRecord(SQLModel, table=True):
    """A single compilation-and-execution session."""

    __tablename__ = "runs"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    spec_name: str
    start_state: str
    start_integrity: str
    alphabet: str  # JSON-encoded list
    total_steps: int = 0
    halted: bool = False
    halt_reason: str | None = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finished_at: str | None = None
    metadata_json: str | None = None  # optional compile metadata


class SnapshotRecord(SQLModel, table=True):
    """One point-in-time machine state within a run."""

    __tablename__ = "snapshots"

    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(index=True)
    step_count: int
    current_state: str
    head_position: int
    read_symbol: str
    write_symbol: str | None = None
    move_direction: str | None = None
    next_state: str | None = None
    tape_window_json: str  # JSON-encoded list of [pos, sym] pairs
    timestamp_utc: str
