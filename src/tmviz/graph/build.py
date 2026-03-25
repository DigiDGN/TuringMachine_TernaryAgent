"""Build the legal office handoff graph."""

from __future__ import annotations

import networkx as nx  # type: ignore[import-untyped]

from tmviz.model import AgentSpec


def build_office_graph(spec: AgentSpec) -> nx.DiGraph:
    """Create a graph containing the authored offices and legal handoffs.

    Nodes are office ids with node attributes describing role/pillar.
    Edges include compile-time hints such as `strengthen_on_success`.
    """

    graph = nx.DiGraph()

    for office in spec.offices:
        graph.add_node(
            office.id,
            role=office.role,
            pillar=office.pillar,
            patch_radius=office.patch_radius,
            can_emit_packets=office.can_emit_packets,
            can_commit_to_tape=office.can_commit_to_tape,
        )

    for path in spec.paths:
        if not path.legal:
            continue
        graph.add_edge(
            path.source,
            path.target,
            label=path.label,
            min_integrity=path.min_integrity,
            max_integrity=path.max_integrity,
            strengthen_on_success=path.strengthen_on_success,
            weaken_on_failure=path.weaken_on_failure,
            preferred_move=path.preferred_move,
            notes=path.notes,
        )

    return graph
