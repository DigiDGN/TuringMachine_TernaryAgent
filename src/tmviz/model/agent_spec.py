"""Top-level ternary agent authoring models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .cells import CellSpec
from .enums import IntegrityMode, OfficeRole
from .offices import OfficeSpec
from .paths import PathSpec

REQUIRED_ROLES = {
    OfficeRole.GENERATOR,
    OfficeRole.ARBITER,
    OfficeRole.CRITIC,
}


class TapeRegionSpec(BaseModel):
    """Named slice of the initial tape."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    start: int
    end: int

    @model_validator(mode="after")
    def validate_bounds(self) -> TapeRegionSpec:
        if self.end < self.start:
            raise ValueError("tape region end must be greater than or equal to start")
        return self


class AgentSpec(BaseModel):
    """High-level authoring model compiled into a flat TM spec."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    blank_symbol: str = Field(default="_", min_length=1)
    alphabet: list[str] = Field(min_length=1)
    initial_tape: list[str]
    initial_head: int = 0
    offices: list[OfficeSpec] = Field(min_length=3, max_length=3)
    paths: list[PathSpec]
    field_seed: list[CellSpec] = Field(default_factory=list)
    tape_regions: list[TapeRegionSpec] = Field(default_factory=list)
    start_office: str = Field(min_length=1)
    start_integrity: IntegrityMode = IntegrityMode.SEED
    start_symbol: str | None = None
    accept_offices: list[str] = Field(default_factory=list)
    reject_offices: list[str] = Field(default_factory=list)
    missing_rule_policy: Literal["halt", "reject", "error"] = "halt"

    @model_validator(mode="after")
    def validate_consistency(self) -> AgentSpec:
        if len(set(self.alphabet)) != len(self.alphabet):
            raise ValueError("alphabet must contain unique symbols")
        if self.blank_symbol not in self.alphabet:
            raise ValueError("blank_symbol must be present in the alphabet")
        if any(symbol not in self.alphabet for symbol in self.initial_tape):
            raise ValueError("initial_tape contains symbols outside the alphabet")

        office_ids = [office.id for office in self.offices]
        if len(set(office_ids)) != len(office_ids):
            raise ValueError("office ids must be unique")

        roles = [office.role for office in self.offices]
        if set(roles) != REQUIRED_ROLES:
            raise ValueError(
                "Phase 1 requires exactly one generator, one arbiter, and one critic office"
            )
        if len(set(roles)) != len(roles):
            raise ValueError(
                "Phase 1 requires exactly one generator, one arbiter, and one critic office"
            )

        office_id_set = set(office_ids)
        if self.start_office not in office_id_set:
            raise ValueError("start_office must reference a defined office")
        if any(
            path.source not in office_id_set or path.target not in office_id_set
            for path in self.paths
        ):
            raise ValueError("every path endpoint must reference a defined office")
        if any(office_id not in office_id_set for office_id in self.accept_offices):
            raise ValueError("accept_offices must reference defined offices")
        if any(office_id not in office_id_set for office_id in self.reject_offices):
            raise ValueError("reject_offices must reference defined offices")
        if set(self.accept_offices).intersection(self.reject_offices):
            raise ValueError("accept_offices and reject_offices must be disjoint")

        if self.start_symbol is not None and self.start_symbol != self.symbol_at_head():
            raise ValueError("start_symbol must match the symbol under the initial head")

        return self

    def symbol_at(self, position: int) -> str:
        """Return the authored symbol at a tape position, defaulting to blank."""

        if 0 <= position < len(self.initial_tape):
            return self.initial_tape[position]
        return self.blank_symbol

    def symbol_at_head(self) -> str:
        """Return the authored symbol under the initial head."""

        return self.symbol_at(self.initial_head)

    def office_by_id(self, office_id: str) -> OfficeSpec:
        """Resolve an office by id."""

        for office in self.offices:
            if office.id == office_id:
                return office
        raise KeyError(office_id)

    def office_by_role(self, role: OfficeRole) -> OfficeSpec:
        """Resolve the unique Phase 1 office for a role."""

        for office in self.offices:
            if office.role is role:
                return office
        raise KeyError(role)
