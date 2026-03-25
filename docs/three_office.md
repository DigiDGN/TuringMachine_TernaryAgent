## Three-Office Prototype

This document describes the minimal three-office prototype and how to run it.

Overview
--------

- Offices: `generator`, `arbiter`, `critic`
- Integrity modes: `death`, `seed`, `life`
- Ternary alphabet: `-1`, `0`, `+1` (blank symbol is `_`)

Files
-----

- `examples/three_office.agent.json` — high-level authored `AgentSpec`.
- `examples/three_office.compiled.json` — compiled flat TM snapshot produced by the compiler.
- `examples/minimal_three_office.compiled.json` — canonical compiled snapshot (updated to match the three-office prototype).

How to compile
--------------

Using the included CLI after an editable install:

```bash
tmviz-compile examples/three_office.agent.json examples/three_office.compiled.json
```

Or run the app pointing at a high-level spec; the factory will compile it before building the runtime:

```bash
python -m tmviz --spec examples/three_office.agent.json
```

What the compiled output is
--------------------------

The compiler flattens `(office × integrity)` into states like `generator__seed`,
and emits a full rule table of 5-tuples in the runtime format:

```text
[current_state, read_symbol, next_state, write_symbol, move_direction]
```

Metadata
--------

Compile-time metadata (e.g. `highways`) is attached under the `metadata`
key in compiled outputs when requested. The runtime validator ignores this
metadata, keeping the runtime schema unchanged.

Notes
-----

This first-pass prototype is intentionally non‑halting (no accept/reject
states). Add terminal conventions in the compiled rules if you want bounded
demo behavior.
