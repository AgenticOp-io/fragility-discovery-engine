from __future__ import annotations

from typing import Protocol

import numpy as np


class BehaviorArchetype(Protocol):
    """Archetypes are deliberately dumb and fast — fuzzing-friendly."""

    name: str

    def redeem_fraction(self, observation: dict[str, float], rng: np.random.Generator) -> float:
        """Return desired aggregate redemption pressure in [0, 1]."""
