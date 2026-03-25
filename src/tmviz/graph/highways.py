"""Compute highway edges from an office graph using reinforcement weights."""

from __future__ import annotations

import copy
import networkx as nx
from typing import Iterable, Tuple


def _edge_score(attrs: dict) -> float:
    """Compute a simple highway score for an edge attrs dict.

    Score favors high `strengthen_on_success` and penalizes large
    `weaken_on_failure`. If `preferred_move` is truthy, give a small bonus.
    """
    s = float(attrs.get("strengthen_on_success", 1.0))
    w = float(attrs.get("weaken_on_failure", 1.0))
    preferred = 1.1 if attrs.get("preferred_move") else 1.0
    # avoid divide-by-zero; larger w reduces score
    denom = max(w, 0.0001)
    return (s / denom) * preferred


def get_highways(graph: nx.DiGraph, threshold: float = 1.05) -> list[Tuple[str, str, dict]]:
    """Return edges considered "highways" with score and rank included.

    Backwards compatible: returns list of (u, v, attrs) tuples as before,
    but `attrs` will include computed keys: `score` (float) and `rank` (int).

    Args:
        graph: a DiGraph with edge attribute 'strengthen_on_success',
               optional 'weaken_on_failure' and 'preferred_move'
        threshold: minimum raw strengthen_on_success (legacy filter)

    Returns:
        list of (source, target, attr_dict) sorted by descending score
    """
    scored: list[tuple[str, str, dict, float]] = []
    for u, v, attrs in graph.edges(data=True):
        s = float(attrs.get("strengthen_on_success", 1.0))
        if s <= threshold:
            continue
        score = _edge_score(attrs)
        scored.append((u, v, copy.deepcopy(attrs), score))

    # sort by score desc
    scored.sort(key=lambda t: t[3], reverse=True)

    # attach rank and normalized score
    if scored:
        max_score = scored[0][3]
    else:
        max_score = 1.0

    out: list[Tuple[str, str, dict]] = []
    for rank, (u, v, attrs, score) in enumerate(scored, start=1):
        attrs["score"] = float(score)
        attrs["rank"] = rank
        # normalized to [0,1]
        attrs["score_normalized"] = float(score / max_score) if max_score else 0.0
        out.append((u, v, attrs))

    return out
