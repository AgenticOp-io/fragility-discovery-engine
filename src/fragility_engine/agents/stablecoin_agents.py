from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class RationalArchetype:
    name: str = "rational"
    backing_trigger: float = 0.97

    def redeem_fraction(self, observation: dict[str, float], rng: np.random.Generator) -> float:
        price = observation["price"]
        if price < self.backing_trigger:
            # Stronger response as backing deteriorates.
            urgency = float(np.clip((self.backing_trigger - price) / 0.08, 0.0, 1.0))
            return float(np.clip(0.15 + 0.85 * urgency, 0.0, 1.0))
        return 0.03


@dataclass
class PanicArchetype:
    name: str = "panic"
    panic_slope: float = 1.4

    def redeem_fraction(self, observation: dict[str, float], rng: np.random.Generator) -> float:
        panic = observation["panic"]
        price = observation["price"]
        base = float(np.clip(self.panic_slope * panic, 0.0, 1.0))
        if price < 0.99:
            base = float(np.clip(base + 0.25, 0.0, 1.0))
        return float(np.clip(base, 0.0, 1.0))


@dataclass
class WhaleArchetype:
    name: str = "whale"
    supply_fraction: float = 0.22
    flee_backing: float = 0.985

    def redeem_fraction(self, observation: dict[str, float], rng: np.random.Generator) -> float:
        price = observation["price"]
        panic = observation["panic"]
        if price < self.flee_backing or panic > 0.55:
            return float(np.clip(self.supply_fraction * 3.6, 0.0, 1.0))
        return 0.02


@dataclass
class AgentPopulation:
    """
    Weighted mixture of archetypes producing aggregate redemption pressure.

    This stays deterministic given `rng` — no LLM policies.
    """

    archetypes: list[tuple[float, RationalArchetype | PanicArchetype | WhaleArchetype]]
    weights: np.ndarray | None = None

    def reset(self, initial_supply: float, rng: np.random.Generator) -> None:
        del initial_supply, rng  # hook for future heterogeneity
        total = sum(w for w, _ in self.archetypes)
        self.weights = np.array([w / total for w, _ in self.archetypes], dtype=np.float64)

    def aggregate_redeem_fraction(self, observation: dict[str, float], rng: np.random.Generator) -> float:
        if self.weights is None:
            raise RuntimeError("Population not initialized; call reset().")
        demands = np.array([a.redeem_fraction(observation, rng) for _, a in self.archetypes], dtype=np.float64)
        return float(np.dot(self.weights, demands))


def default_stablecoin_population() -> AgentPopulation:
    return AgentPopulation(
        archetypes=[
            (0.62, RationalArchetype()),
            (0.28, PanicArchetype()),
            (0.10, WhaleArchetype()),
        ]
    )
