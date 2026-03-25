"""Public compile surface for high-level ternary agents."""

from .machine import (
    CompiledMachine,
    compile_agent_mapping,
    compile_agent_spec,
    is_agent_spec_mapping,
)

__all__ = [
    "CompiledMachine",
    "compile_agent_mapping",
    "compile_agent_spec",
    "is_agent_spec_mapping",
]
