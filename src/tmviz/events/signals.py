"""Centralized Blinker signal registry.

All named signals for the tmviz system are obtained through ``get_signal``.
When ``blinker`` is installed, real :class:`blinker.NamedSignal` instances are
returned.  Otherwise a lightweight no-op :class:`DummySignal` is used so that
call-sites never need to guard imports.
"""

from __future__ import annotations

from typing import Any


class DummySignal:
    """No-op stand-in when blinker is not installed."""

    def __init__(self, name: str) -> None:
        self.name = name

    def send(self, *_args: Any, **_kwargs: Any) -> list[Any]:
        return []

    def connect(self, receiver: Any, **_kwargs: Any) -> Any:
        return receiver

    def disconnect(self, receiver: Any, **_kwargs: Any) -> None:
        pass


try:
    import blinker as _blinker

    def get_signal(name: str) -> Any:
        """Return a :class:`blinker.NamedSignal` for *name*."""
        return _blinker.signal(name)

except ImportError:

    def get_signal(name: str) -> DummySignal:  # type: ignore[misc]
        """Return a no-op :class:`DummySignal` (blinker not installed)."""
        return DummySignal(name)


# ── Compile-time signals ─────────────────────────────────────────────

compile_started = get_signal("tmviz.compile.started")
compile_highways = get_signal("tmviz.compile.highways")
compile_finished = get_signal("tmviz.compile.finished")

# ── Runtime signals ──────────────────────────────────────────────────

step_committed = get_signal("tmviz.step.committed")
machine_halted = get_signal("tmviz.machine.halted")

# ── Trace signals ────────────────────────────────────────────────────

trace_started = get_signal("tmviz.trace.started")
trace_flushed = get_signal("tmviz.trace.flushed")
