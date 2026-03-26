import pytest

from tmviz.model.enums import IntegrityMode
from tmviz.compiler.rules import next_integrity
from tmviz.compiler import compile_agent_mapping
from tmviz.domain.exceptions import SpecValidationError


def test_next_integrity_transitions():
    # death + write -1 stays death
    assert next_integrity(IntegrityMode.DEATH, "-1") is IntegrityMode.DEATH

    # write 0 -> seed
    assert next_integrity(IntegrityMode.LIFE, "0") is IntegrityMode.SEED

    # write +1 -> life
    assert next_integrity(IntegrityMode.SEED, "+1") is IntegrityMode.LIFE

    # other writes preserve current
    assert next_integrity(IntegrityMode.SEED, "_") is IntegrityMode.SEED


def test_compile_raises_on_illegal_handoff():
    # minimal spec with offices but missing generator->arbiter path
    raw = {
        "name": "illegal_handoff",
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
        # intentionally empty paths -> illegal handoffs
        "paths": [],
        "start_office": "generator",
        "start_integrity": "seed",
        "accept_offices": [],
        "reject_offices": [],
    }

    with pytest.raises(SpecValidationError):
        compile_agent_mapping(raw).to_mapping()
