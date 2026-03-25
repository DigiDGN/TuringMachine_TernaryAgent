"""Path models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import INTEGRITY_RANK, IntegrityMode, MoveIntent


class PathSpec(BaseModel):
    """A legal office handoff with compile-time hints."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    label: str = Field(min_length=1)
    legal: bool = True
    min_integrity: IntegrityMode | None = None
    max_integrity: IntegrityMode | None = None
    strengthen_on_success: float = Field(default=1.0, gt=0.0)
    weaken_on_failure: float = Field(default=1.0, gt=0.0)
    preferred_move: MoveIntent = MoveIntent.NEXT
    notes: str | None = None

    @model_validator(mode="after")
    def validate_integrity_window(self) -> PathSpec:
        if (
            self.min_integrity is not None
            and self.max_integrity is not None
            and INTEGRITY_RANK[self.min_integrity] > INTEGRITY_RANK[self.max_integrity]
        ):
            raise ValueError("min_integrity must be less than or equal to max_integrity")
        return self

