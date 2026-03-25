"""Compute highway edges from an office graph using reinforcement weights."""

from __future__ import annotations

import networkx as nx
from typing import Iterable, Tuple


def get_highways(graph: nx.DiGraph, threshold: float = 1.05) -> list[Tuple[str, str, dict]]:
    """Return edges whose strengthen_on_success exceeds the threshold.

    Args:
        graph: a DiGraph with edge attribute 'strengthen_on_success'
        threshold: minimum strength to include

    Returns:
        list of (source, target, attr_dict)
    """
    out = []
    for u, v, attrs in graph.edges(data=True):
        s = attrs.get("strengthen_on_success", 1.0)
        if s > threshold:
            out.append((u, v, attrs))
    return out
