"""Generate compiled TM artifacts for authored example agent specs.

Writes files next to each `*.agent.json` with suffix `.compiled.json`.
"""

from __future__ import annotations

import json
from pathlib import Path

from tmviz.compiler import compile_agent_mapping
from tmviz.compile.emit_json import emit_compiled_to_path


def main(example_dir: str | Path | None = None) -> int:
    base = Path(example_dir or Path.cwd() / "examples")
    if not base.exists():
        print(f"examples directory not found: {base}")
        return 1

    files = list(base.glob("*.agent.json"))
    if not files:
        print("No .agent.json files found in examples/")
        return 0

    for p in files:
        raw = json.loads(p.read_text(encoding="utf8"))
        compiled = compile_agent_mapping(raw)
        out_path = p.with_suffix(".compiled.json")
        emit_compiled_to_path(compiled, out_path)
        print(f"Wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
