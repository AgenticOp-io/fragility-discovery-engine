"""Installable BYOW tutorial worlds (not charter reference domains)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from fragility_engine.byow.examples import capacity_pool, token_bucket
from fragility_engine.types import RolloutResult


@dataclass(frozen=True)
class ExampleWorldSpec:
    name: str
    description: str
    make_world: Callable[[], Any]
    rollout: Callable[[Any, np.ndarray, int], RolloutResult]
    default_horizon: int = 16


EXAMPLES: dict[str, ExampleWorldSpec] = {
    "capacity-pool": ExampleWorldSpec(
        name="capacity-pool",
        description="Bounded pool under surge + leak timing (connection-pool analogy).",
        make_world=capacity_pool.make_world,
        rollout=capacity_pool.rollout,
        default_horizon=16,
    ),
    "token-bucket": ExampleWorldSpec(
        name="token-bucket",
        description="Token bucket with arrival bursts and drain shocks (rate-limit analogy).",
        make_world=token_bucket.make_world,
        rollout=token_bucket.rollout,
        default_horizon=14,
    ),
}


def get_example(name: str) -> ExampleWorldSpec:
    key = name.strip().lower()
    if key not in EXAMPLES:
        known = ", ".join(sorted(EXAMPLES))
        raise KeyError(f"Unknown example {name!r}; choose from: {known}")
    return EXAMPLES[key]


def list_examples() -> list[str]:
    return sorted(EXAMPLES)
