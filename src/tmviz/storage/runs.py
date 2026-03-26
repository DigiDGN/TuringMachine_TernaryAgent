"""Run lifecycle: create, record snapshots, finish, query."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from tmviz.trace.snapshot import MachineSnapshot

from .engine import get_engine, init_db
from .models import RunRecord, SnapshotRecord


class RunStore:
    """High-level API for persisting and querying machine runs."""

    def __init__(self, db_path: str | None = None) -> None:
        from .engine import reset_engine

        reset_engine()
        self._engine = get_engine(db_path)
        init_db(self._engine)

    # ── write path ───────────────────────────────────────────────

    def create_run(
        self,
        name: str,
        spec_name: str,
        start_state: str,
        start_integrity: str,
        alphabet: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Create a new run record and return its id."""

        record = RunRecord(
            name=name,
            spec_name=spec_name,
            start_state=start_state,
            start_integrity=start_integrity,
            alphabet=json.dumps(alphabet),
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        with Session(self._engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            assert record.id is not None
            return record.id

    def record_snapshot(self, run_id: int, snapshot: MachineSnapshot) -> None:
        """Append a snapshot to a run."""

        record = SnapshotRecord(
            run_id=run_id,
            step_count=snapshot.step_count,
            current_state=snapshot.current_state,
            head_position=snapshot.head_position,
            read_symbol=snapshot.read_symbol,
            write_symbol=snapshot.write_symbol,
            move_direction=snapshot.move_direction,
            next_state=snapshot.next_state,
            tape_window_json=json.dumps(
                [list(cell) for cell in snapshot.tape_window]
            ),
            timestamp_utc=snapshot.timestamp_utc,
        )
        with Session(self._engine) as session:
            session.add(record)
            session.commit()

    def finish_run(
        self,
        run_id: int,
        total_steps: int,
        halted: bool = False,
        halt_reason: str | None = None,
    ) -> None:
        """Mark a run as finished."""

        with Session(self._engine) as session:
            record = session.get(RunRecord, run_id)
            if record is None:
                raise KeyError(f"run {run_id} not found")
            record.total_steps = total_steps
            record.halted = halted
            record.halt_reason = halt_reason
            record.finished_at = datetime.now(timezone.utc).isoformat()
            session.add(record)
            session.commit()

    # ── read path ────────────────────────────────────────────────

    def list_runs(self, limit: int = 20) -> list[RunRecord]:
        """Return the most recent runs, newest first."""

        with Session(self._engine) as session:
            statement = (
                select(RunRecord)
                .order_by(RunRecord.created_at.desc())  # type: ignore[union-attr]
                .limit(limit)
            )
            return list(session.exec(statement).all())

    def get_run(self, run_id: int) -> RunRecord | None:
        """Fetch a single run by id."""

        with Session(self._engine) as session:
            return session.get(RunRecord, run_id)

    def get_snapshots(
        self, run_id: int, offset: int = 0, limit: int = 100
    ) -> list[SnapshotRecord]:
        """Fetch snapshots for a run, ordered by step_count."""

        with Session(self._engine) as session:
            statement = (
                select(SnapshotRecord)
                .where(SnapshotRecord.run_id == run_id)
                .order_by(SnapshotRecord.step_count)  # type: ignore[arg-type]
                .offset(offset)
                .limit(limit)
            )
            return list(session.exec(statement).all())

    def snapshot_count(self, run_id: int) -> int:
        """Return the number of snapshots stored for a run."""

        with Session(self._engine) as session:
            from sqlmodel import func

            statement = select(func.count()).where(
                SnapshotRecord.run_id == run_id
            )
            return session.exec(statement).one()

    def to_machine_snapshot(self, record: SnapshotRecord) -> MachineSnapshot:
        """Convert a stored record back to a MachineSnapshot."""

        return MachineSnapshot(
            step_count=record.step_count,
            current_state=record.current_state,
            head_position=record.head_position,
            read_symbol=record.read_symbol,
            write_symbol=record.write_symbol,
            move_direction=record.move_direction,
            next_state=record.next_state,
            tape_window=tuple(
                tuple(cell) for cell in json.loads(record.tape_window_json)
            ),
            timestamp_utc=record.timestamp_utc,
        )
