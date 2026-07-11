"""Bring-your-own-world adapter helpers (Phase R)."""

from fragility_engine.byow.check import check_rollout_determinism
from fragility_engine.byow.examples import ExampleWorldSpec, get_example, list_examples
from fragility_engine.byow.rollout import run_rollout
from fragility_engine.world.base import WorldProtocol

__all__ = [
    "WorldProtocol",
    "ExampleWorldSpec",
    "check_rollout_determinism",
    "get_example",
    "list_examples",
    "run_rollout",
]
