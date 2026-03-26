# Phase 2: Blinker Signals, structlog Traces, NDJSON Replay

## Context

Phase 1 delivered the high-level AgentSpec authoring model, the compiler that
flattens `office x integrity` into flat TM states, the graph module for handoff
legality and highway scoring, and the CLI. All 40 tests pass.

Phase 2 adds the observability and event infrastructure that the design document
specified as the second ordered layer:

- Centralized Blinker signal registry
- Proper structlog configuration
- Point-in-time machine snapshots
- NDJSON file-based trace replay

## Housekeeping

### Fix `graph/__init__.py`

The file currently has duplicate import blocks (two `__all__` declarations).
Consolidate into a single block exporting: `build_office_graph`,
`get_highways`, `integrity_allowed`, `resolve_handoff_move`.

### Remove `compile/` legacy module

`src/tmviz/compile/` duplicates `src/tmviz/compiler/` with looser types and no
graph integration. No imports in the codebase reference it (all tests and the
factory use `tmviz.compiler`). Delete the entire `compile/` package.

## New Modules

### `events/signals.py` -- Blinker Signal Registry

Central registry for all named Blinker signals. Graceful fallback to a no-op
`DummySignal` when blinker is not installed.

Signals defined:

| Signal name                  | Sender context     | kwargs                          |
|------------------------------|--------------------|---------------------------------|
| `tmviz.compile.started`     | compiler           | name, spec                      |
| `tmviz.compile.highways`    | compiler           | name, highways                  |
| `tmviz.compile.finished`    | compiler           | name, mapping                   |
| `tmviz.step.committed`      | step service       | snapshot (MachineSnapshot)      |
| `tmviz.machine.halted`      | step service       | name, reason, state             |
| `tmviz.trace.started`       | trace writer       | path                            |
| `tmviz.trace.flushed`       | trace writer       | path, count                     |

Public API:

```python
def get_signal(name: str) -> Signal | DummySignal
```

### `trace/logger.py` -- structlog Configuration

Single entry point `configure_logging(level, json_output)` that sets up:

- Timestamper (ISO 8601 UTC)
- Log level filter
- JSON renderer using orjson when available, stdlib json fallback
- stdlib logging integration (structlog wraps stdlib loggers)

Public API:

```python
def configure_logging(level: str = "INFO", json_output: bool = False) -> None
def get_logger(name: str) -> BoundLogger
```

### `trace/snapshot.py` -- MachineSnapshot

Frozen dataclass capturing one point-in-time machine state:

```python
@dataclass(frozen=True, slots=True)
class MachineSnapshot:
    step_count: int
    current_state: str
    head_position: int
    read_symbol: str
    write_symbol: str | None
    move_direction: str | None
    next_state: str | None
    tape_window: tuple[tuple[int, str], ...]
    timestamp_utc: str  # ISO 8601

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MachineSnapshot: ...
```

Factory function:

```python
def capture(machine: TuringMachine, rule: Rule | None = None) -> MachineSnapshot
```

### `trace/replay.py` -- NDJSON TraceWriter and TraceReader

**TraceWriter**: Appends one JSON line per snapshot to a file. Supports context
manager protocol. Subscribes to `tmviz.step.committed` signal when
`auto_subscribe=True`.

```python
class TraceWriter:
    def __init__(self, path: Path, auto_subscribe: bool = True) -> None
    def write(self, snapshot: MachineSnapshot) -> None
    def flush(self) -> None
    def close(self) -> None
    def __enter__(self) / __exit__(): ...
```

**TraceReader**: Reads NDJSON trace files. Supports forward iteration and
random access by step index.

```python
class TraceReader:
    def __init__(self, path: Path) -> None
    def __iter__(self) -> Iterator[MachineSnapshot]
    def __len__(self) -> int
    def __getitem__(self, index: int) -> MachineSnapshot
```

File format: one JSON object per line, each produced by
`MachineSnapshot.to_dict()`. Uses orjson if available for serialization,
stdlib json otherwise.

## Integration

### Compiler signals

`compiler/machine.py` replaces its inline signal definitions with imports from
`events.signals`. The `_signal()` helper and `_DummySignal` class move to
`events/signals.py`.

### Controller trace wiring

The `StepService` emits `tmviz.step.committed` after each successful commit,
passing the captured `MachineSnapshot`. This is opt-in: the signal fires
regardless, but nothing listens unless a `TraceWriter` is attached.

## Dependencies

- Move `blinker>=1.6,<2` from dev to main dependencies
- Move `structlog>=24,<25` from dev to main dependencies
- Add `orjson>=3,<4` as optional dependency (extra named `fast`)

## Tests

| Test file                         | Coverage target                              |
|-----------------------------------|----------------------------------------------|
| `test_signals.py`                | get_signal, send/receive, DummySignal fallback|
| `test_snapshot.py`               | capture(), to_dict/from_dict roundtrip        |
| `test_trace_replay.py`           | write N snapshots, read back, verify NDJSON   |
| `test_trace_integration.py`      | run machine 10 steps with TraceWriter, verify |
| existing tests                    | all 40 must continue to pass                  |
