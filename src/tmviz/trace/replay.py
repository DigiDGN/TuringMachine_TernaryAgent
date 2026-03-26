"""NDJSON trace writer and reader.

Each line in a trace file is a JSON-encoded :class:`MachineSnapshot` dict.
Uses ``orjson`` for serialization when available, falling back to :mod:`json`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from tmviz.events.signals import step_committed, trace_flushed, trace_started

from .snapshot import MachineSnapshot

# ── JSON helpers ─────────────────────────────────────────────────────

try:
    import orjson

    def _dumps(obj: dict[str, Any]) -> bytes:
        return orjson.dumps(obj)

    def _loads(raw: bytes | str) -> dict[str, Any]:
        return orjson.loads(raw)

except ImportError:

    def _dumps(obj: dict[str, Any]) -> bytes:  # type: ignore[misc]
        return json.dumps(obj, ensure_ascii=False).encode("utf-8")

    def _loads(raw: bytes | str) -> dict[str, Any]:  # type: ignore[misc]
        return json.loads(raw)


# ── TraceWriter ──────────────────────────────────────────────────────


class TraceWriter:
    """Append machine snapshots to an NDJSON file.

    Parameters
    ----------
    path:
        Destination file.  Created (with parents) on first write.
    auto_subscribe:
        When *True*, automatically subscribes to the
        ``tmviz.step.committed`` signal so that snapshots are written
        without manual calls.
    """

    def __init__(self, path: Path | str, auto_subscribe: bool = False) -> None:
        self._path = Path(path)
        self._fh = None
        self._count = 0
        if auto_subscribe:
            step_committed.connect(self._on_step_committed)

    # ── public API ───────────────────────────────────────────────

    def write(self, snapshot: MachineSnapshot) -> None:
        """Append one snapshot line."""

        if self._fh is None:
            self._open()
        assert self._fh is not None
        self._fh.write(_dumps(snapshot.to_dict()))
        self._fh.write(b"\n")
        self._count += 1

    def flush(self) -> None:
        """Flush buffered data to disk."""

        if self._fh is not None:
            self._fh.flush()
            trace_flushed.send(path=str(self._path), count=self._count)

    def close(self) -> None:
        """Flush and close the underlying file."""

        if self._fh is not None:
            self.flush()
            self._fh.close()
            self._fh = None
        step_committed.disconnect(self._on_step_committed)

    # ── context manager ──────────────────────────────────────────

    def __enter__(self) -> TraceWriter:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # ── internals ────────────────────────────────────────────────

    def _open(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self._path, "ab")
        trace_started.send(path=str(self._path))

    def _on_step_committed(self, *_args: Any, **kwargs: Any) -> None:
        snapshot = kwargs.get("snapshot")
        if isinstance(snapshot, MachineSnapshot):
            self.write(snapshot)


# ── TraceReader ──────────────────────────────────────────────────────


class TraceReader:
    """Read machine snapshots from an NDJSON trace file.

    Supports forward iteration and random access by step index.
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._lines: list[bytes] | None = None

    def __iter__(self) -> Iterator[MachineSnapshot]:
        """Iterate snapshots in file order."""

        for line in self._raw_lines():
            if line.strip():
                yield MachineSnapshot.from_dict(_loads(line))

    def __len__(self) -> int:
        """Return the number of snapshots in the trace."""

        return len(self._raw_lines())

    def __getitem__(self, index: int) -> MachineSnapshot:
        """Random access by step index."""

        lines = self._raw_lines()
        return MachineSnapshot.from_dict(_loads(lines[index]))

    def _raw_lines(self) -> list[bytes]:
        """Lazily load and cache raw lines (excluding blanks)."""

        if self._lines is None:
            with open(self._path, "rb") as fh:
                self._lines = [ln for ln in fh.readlines() if ln.strip()]
        return self._lines
