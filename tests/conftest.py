"""Shared test fixtures."""

import pytest

MINIMAL_AGENT = {
    "name": "minimal_three_office",
    "blank_symbol": "_",
    "alphabet": ["-1", "0", "+1", "_"],
    "initial_tape": ["_"],
    "initial_head": 0,
    "offices": [
        {
            "id": "generator",
            "role": "generator",
            "pillar": "right",
            "title": "Generator",
            "description": "spawn",
            "patch_radius": 1,
            "can_emit_packets": True,
            "can_commit_to_tape": False,
            "semantics": {
                "healthy_label": "useful",
                "latent_label": "waiting",
                "corrupt_label": "hallucinating",
                "healthy_description": "prod",
                "latent_description": "wait",
                "corrupt_description": "bad",
            },
        },
        {
            "id": "arbiter",
            "role": "arbiter",
            "pillar": "center",
            "title": "Arbiter",
            "description": "stabilize",
            "patch_radius": 1,
            "can_emit_packets": False,
            "can_commit_to_tape": True,
            "semantics": {
                "healthy_label": "coherent",
                "latent_label": "pending",
                "corrupt_label": "false_balance",
                "healthy_description": "synth",
                "latent_description": "pending",
                "corrupt_description": "fake",
            },
        },
        {
            "id": "critic",
            "role": "critic",
            "pillar": "left",
            "title": "Critic",
            "description": "prune",
            "patch_radius": 1,
            "can_emit_packets": False,
            "can_commit_to_tape": False,
            "semantics": {
                "healthy_label": "bounded",
                "latent_label": "unsure",
                "corrupt_label": "paralyzed",
                "healthy_description": "filter",
                "latent_description": "unsure",
                "corrupt_description": "stuck",
            },
        },
    ],
    "paths": [
        {
            "source": "generator",
            "target": "arbiter",
            "label": "propose",
            "legal": True,
            "strengthen_on_success": 1.2,
            "weaken_on_failure": 1.0,
            "preferred_move": "next",
        },
        {
            "source": "arbiter",
            "target": "critic",
            "label": "needs_check",
            "legal": True,
            "strengthen_on_success": 1.1,
            "weaken_on_failure": 1.2,
            "preferred_move": "prev",
        },
        {
            "source": "critic",
            "target": "arbiter",
            "label": "back",
            "legal": True,
            "strengthen_on_success": 1.2,
            "weaken_on_failure": 1.0,
            "preferred_move": "next",
        },
        {
            "source": "arbiter",
            "target": "generator",
            "label": "retry",
            "legal": True,
            "strengthen_on_success": 1.0,
            "weaken_on_failure": 1.1,
            "preferred_move": "next",
        },
    ],
    "start_office": "generator",
    "start_integrity": "seed",
    "accept_offices": [],
    "reject_offices": [],
}


@pytest.fixture
def minimal_agent():
    """Return the canonical minimal three-office agent spec dict."""
    return dict(MINIMAL_AGENT)
