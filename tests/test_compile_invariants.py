from tmviz.compiler import compile_agent_mapping
from tmviz.graph import build_office_graph, get_highways

from conftest import MINIMAL_AGENT


def test_compile_invariants():
    compiled = compile_agent_mapping(MINIMAL_AGENT)

    # states unique
    assert len(set(compiled.states)) == len(compiled.states)

    alphabet = set(compiled.alphabet)

    # start exists
    assert compiled.start_state in compiled.states

    # rules validity
    for rule in compiled.rules:
        current, read, nxt, write, move = rule
        assert current in compiled.states
        assert nxt in compiled.states
        assert read in alphabet
        assert write in alphabet
        assert move in {"L", "R", "S"}


def test_graph_highways():
    # ensure build_office_graph and get_highways work
    from tmviz.model.agent_spec import AgentSpec

    spec = AgentSpec.model_validate(MINIMAL_AGENT)
    g = build_office_graph(spec)
    assert g.has_node("generator") and g.has_node("arbiter") and g.has_node("critic")

    highways = get_highways(g, threshold=1.15)
    # generator->arbiter and critic->arbiter have strength 1.2 and should appear
    edges = {(u, v) for u, v, _ in highways}
    assert ("generator", "arbiter") in edges
    assert ("critic", "arbiter") in edges
