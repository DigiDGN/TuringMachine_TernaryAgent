from tmviz.factory.machine_factory import MachineSpecFactory
from tmviz.compiler import compile_agent_mapping
from tests.test_compile_invariants import MINIMAL_AGENT


def test_inductive_generator_creates_nonblank_symbols():
    factory = MachineSpecFactory()
    compiled = compile_agent_mapping(MINIMAL_AGENT)
    machine = factory.from_mapping(compiled.to_mapping())

    steps = 50
    for _ in range(steps):
        if machine.halted:
            break
        machine.step()

    # after some steps, expect at least one non-blank symbol on the tape
    window = machine.preview_window(radius=20)
    symbols = [sym for _, sym in window]
    assert "+1" in symbols or "-1" in symbols or "0" in symbols
