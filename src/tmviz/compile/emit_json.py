"""Emit compiled machine JSON artifacts for downstream tooling."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def emit_compiled_json(mapping: dict[str, Any], path: Path | str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf8") as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=2)


def emit_compiled_to_path(compiled, path: Path | str) -> None:
    """Convenience wrapper accepting either CompiledMachine or mapping."""
    if hasattr(compiled, "to_mapping"):
        try:
            mapping = compiled.to_mapping(include_metadata=True)
        except TypeError:
            mapping = compiled.to_mapping()
    else:
        mapping = dict(compiled)
    emit_compiled_json(mapping, path)
