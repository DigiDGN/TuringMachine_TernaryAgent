"""Field cell models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .enums import PatchKind, TernaryValue


class CellSpec(BaseModel):
    """Typed authoring model for a field cell."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    kind: PatchKind
    ternary_value: TernaryValue = TernaryValue.ZERO
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    provenance: str | None = None
    age: int = Field(default=0, ge=0)
    links: list[str] = Field(default_factory=list)

