"""Validate legal office handoffs."""

from __future__ import annotations

import networkx as nx  # type: ignore[import-untyped]

from tmviz.domain.exceptions import SpecValidationError
from tmviz.model import IntegrityMode, MoveIntent
from tmviz.model.enums import INTEGRITY_RANK


def integrity_allowed(
    current: IntegrityMode,
    min_integrity: IntegrityMode | None,
    max_integrity: IntegrityMode | None,
) -> bool:
    """Return whether a handoff allows the current integrity mode."""

    current_rank = INTEGRITY_RANK[current]
    if min_integrity is not None and current_rank < INTEGRITY_RANK[min_integrity]:
        return False
    if max_integrity is not None and current_rank > INTEGRITY_RANK[max_integrity]:
        return False
    return True


def resolve_handoff_move(
    graph: nx.DiGraph,
    source: str,
    target: str,
    integrity: IntegrityMode,
) -> MoveIntent | None:
    """Resolve the preferred move for a legal handoff."""

    if source == target:
        return None
    if not graph.has_edge(source, target):
        raise SpecValidationError(f"illegal office handoff: {source} -> {target}")

    edge_data = graph.edges[source, target]
    min_integrity = edge_data.get("min_integrity")
    max_integrity = edge_data.get("max_integrity")
    if not integrity_allowed(
        current=integrity,
        min_integrity=min_integrity,
        max_integrity=max_integrity,
    ):
        raise SpecValidationError(
            f"office handoff {source} -> {target} is not allowed for integrity={integrity.value!r}"
        )

    preferred_move = edge_data.get("preferred_move")
    if not isinstance(preferred_move, MoveIntent):
        raise SpecValidationError(
            f"office handoff {source} -> {target} is missing a preferred move"
        )
    return preferred_move
