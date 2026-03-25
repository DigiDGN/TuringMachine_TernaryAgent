# Contribution and Testing Guide

[Back to README](../README.md) | [User Guide](user-guide.md) | [Spec Reference](spec-reference.md) | [Architecture Guide](architecture.md)

## Prerequisites

- Python `3.12`
- a local virtual environment at `.venv`

The project currently targets:

- `networkx`
- `pydantic`
- `pygame-ce`
- `transitions`
- `pytest`
- `ruff`

## Local Setup

### Windows

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
```

### Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .[dev]
```

## Day-To-Day Commands

Run the simulator:

```bash
python -m tmviz
```

Run tests:

```bash
pytest -q
```

Run lint:

```bash
ruff check
```

Run type checks:

```bash
mypy src
```

## Where To Change Things

| Area | Place to start |
| --- | --- |
| Machine semantics | `src/tmviz/domain/` |
| High-level agent models | `src/tmviz/model/` |
| High-level graph/compiler logic | `src/tmviz/graph/`, `src/tmviz/compiler/` |
| App state machine and commands | `src/tmviz/app/` |
| JSON spec validation and loading | `src/tmviz/factory/` |
| Event bus and logging | `src/tmviz/infra/` |
| Rendering, layout, and input | `src/tmviz/ui/` |
| Raw runtime example machines | `specs/` |
| High-level authoring examples | `examples/` |
| Automated coverage | `tests/` |

## Adding A New Bundled Spec

1. Add a JSON file under `specs/`.
2. Follow the schema described in [Spec Reference](spec-reference.md).
3. Keep the machine small enough to understand visually unless complexity is the point.
4. Run `pytest -q` to confirm it loads with the existing spec tests.
5. Update docs if the new machine should be surfaced as a recommended example.

## Adding A High-Level Authoring Example

1. Add the authored agent JSON and compiled TM snapshot under `examples/`.
2. Do not place high-level authoring files in top-level `specs/`; the app still
   uses `specs/` as its bundled raw runtime TM set.
3. Verify the authored file compiles through `tmviz.compiler.compile_agent_mapping`.
4. Update tests or snapshots if the compiled output is part of the public example surface.
5. Update docs if the example should be discoverable from README or the spec reference.

## Testing Expectations

At a minimum, changes should preserve:

- domain correctness
- high-level model and compiler correctness when those packages are touched
- controller lifecycle behavior
- spec loading and validation
- UI layout and renderer smoke coverage

Useful existing test areas:

- domain engine tests
- compiler and authoring model tests
- controller tests
- spec loading tests
- UI layout tests
- renderer smoke tests

## Documentation Expectations

Documentation is part of the product surface.

If you change any of the following, update the docs in the same change:

- keyboard controls
- bundled machines
- machine-spec schema or validation rules
- architecture or package boundaries
- install, test, or lint commands
- visible UI structure or terminology

## Suggested Contribution Checklist

- code matches the current architecture
- tests pass locally
- lint passes locally
- mypy passes locally
- `python -m tmviz --help` succeeds
- spec examples are valid
- README and `docs/` still reflect the real behavior
- screenshots are refreshed if the visible UI changed materially
- GitHub Actions CI is expected to pass on Python `3.12`
