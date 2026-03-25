"""Minimal CLI to compile AgentSpec files into flat TM JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tmviz.compiler import compile_agent_mapping


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tmviz-compile")
    parser.add_argument("spec", help="Path to agent spec (JSON)")
    parser.add_argument("out", nargs="?", help="Output file (defaults to stdout)")
    args = parser.parse_args(argv)

    spec_path = Path(args.spec)
    raw = json.loads(spec_path.read_text(encoding="utf8"))
    compiled_obj = compile_agent_mapping(raw)
    try:
        compiled = compiled_obj.to_mapping(include_metadata=True)
    except TypeError:
        compiled = compiled_obj.to_mapping()

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(compiled, ensure_ascii=False, indent=2), encoding="utf8")
    else:
        print(json.dumps(compiled, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
