"""Installable falsification tutorial examples."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from fragility_engine.falsify.examples import ranked_store
from fragility_engine.types import RolloutResult


@dataclass(frozen=True)
class FalsificationExampleSpec:
    name: str
    description: str
    make_world: Callable[[], Any]
    rollout: Callable[[Any, np.ndarray, int], RolloutResult]
    default_horizon: int = 14


EXAMPLES: dict[str, FalsificationExampleSpec] = {
    "ranked-store": FalsificationExampleSpec(
        name="ranked-store",
        description="Ranked retrieval invariant: stale records must not appear in top-k.",
        make_world=ranked_store.make_world,
        rollout=ranked_store.rollout,
        default_horizon=14,
    ),
}


def get_example(name: str) -> FalsificationExampleSpec:
    key = name.strip().lower()
    if key not in EXAMPLES:
        known = ", ".join(sorted(EXAMPLES))
        raise KeyError(f"Unknown falsification example {name!r}; choose from: {known}")
    return EXAMPLES[key]


def list_examples() -> list[str]:
    return sorted(EXAMPLES)
