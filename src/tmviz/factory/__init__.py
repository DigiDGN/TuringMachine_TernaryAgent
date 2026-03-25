"""Factory utilities for building machines from specs."""

from .spec_models import MachineSpec

__all__ = ["MachineSpec", "MachineSpecFactory"]


def __getattr__(name: str) -> object:
    if name == "MachineSpecFactory":
        from .machine_factory import MachineSpecFactory

        return MachineSpecFactory
    raise AttributeError(name)

