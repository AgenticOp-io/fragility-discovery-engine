"""Falsification / red-team harness (Phase S)."""

from fragility_engine.falsify.examples import FalsificationExampleSpec, get_example, list_examples
from fragility_engine.falsify.protocol import HARNESS_KIND, FalsificationWorldProtocol, SnapshotMixin
from fragility_engine.falsify.rollout import replay_meta_for_falsification, run_falsification_rollout

__all__ = [
    "FalsificationExampleSpec",
    "FalsificationWorldProtocol",
    "HARNESS_KIND",
    "SnapshotMixin",
    "get_example",
    "list_examples",
    "replay_meta_for_falsification",
    "run_falsification_rollout",
]
