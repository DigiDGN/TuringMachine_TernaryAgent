"""Office models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .enums import OfficeRole, PillarBias


class OfficeModeSemantics(BaseModel):
    """Human-readable mode semantics for an office."""

    model_config = ConfigDict(extra="forbid")

    healthy_label: str = Field(min_length=1)
    latent_label: str = Field(min_length=1)
    corrupt_label: str = Field(min_length=1)
    healthy_description: str = Field(min_length=1)
    latent_description: str = Field(min_length=1)
    corrupt_description: str = Field(min_length=1)


class OfficeSpec(BaseModel):
    """A cognitive office in the high-level authoring model."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    role: OfficeRole
    pillar: PillarBias
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    patch_radius: int = Field(default=1, ge=0)
    can_emit_packets: bool = False
    can_commit_to_tape: bool = False
    semantics: OfficeModeSemantics

