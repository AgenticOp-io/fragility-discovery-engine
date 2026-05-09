from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from fragility_engine.types import ExogenousEvent, TrajectoryStep


@dataclass(frozen=True)
class WorldConfig:
    """Shared knobs; domains subclass or extend via their own config dataclass."""

    max_steps: int = 48


class WorldProtocol(Protocol):
    """Worlds expose explicit vectors for logging / attribution."""

    def step(
        self,
        events: tuple[ExogenousEvent, ...],
        rng: np.random.Generator,
    ) -> TrajectoryStep:
        ...

    def state_vector(self) -> np.ndarray:
        ...

    def instability_score(self) -> float:
        ...

    def is_collapsed(self) -> bool:
        ...
