"""Phase O — inventory buffer / stockout stress (sixth reference domain, same shock encoding)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.agents.stablecoin_agents import AgentPopulation
from fragility_engine.types import ExogenousEvent, TrajectoryStep


@dataclass
class InventoryBufferWorld:
    """
    Normalized stock level ``S`` and fulfillment capacity ``F`` (both in ``[0,1]``).

    ``reserve_loss`` shocks drain stock (demand spikes); ``rumor`` shocks erode fulfillment
    (supplier / logistics trust). Distinct from service backlog (queue depth) and peg worlds.
    """

    population: AgentPopulation
    demand_spike_gain: float = 0.88
    fulfillment_erosion: float = 0.14
    replenish_rate: float = 0.36
    stock_recovery: float = 0.045
    stockout_collapse: float = 0.09
    fulfillment_floor_collapse: float = 0.11
    recovery_stock: float = 0.78
    max_steps: int = 26
    _S: float = 0.9
    _F: float = 0.93
    _timestep: int = 0

    @property
    def depeg_threshold(self) -> float:
        return float(self.recovery_stock)

    def reset(self, *, initial_stock: float = 0.88, stock_scale: float = 1.0) -> None:
        boost = float(np.clip(stock_scale, 1.0, 1.5))
        self._S = float(np.clip(float(initial_stock) * boost, 0.0, 1.0))
        self._F = 0.93
        self._timestep = 0

    def state_vector(self) -> np.ndarray:
        return np.array([self._S, self._F, 1.0 - self._S, float(self._timestep)], dtype=np.float64)

    def instability_score(self) -> float:
        return float(0.5 * (1.0 - self._S) + 0.5 * (1.0 - self._F))

    def is_collapsed(self) -> bool:
        return bool(self._S <= self.stockout_collapse or self._F <= self.fulfillment_floor_collapse)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        for ev in events:
            if ev.kind == "reserve_loss":
                mag = float(np.clip(ev.magnitude, 0.0, 1.0))
                self._S -= float(self.demand_spike_gain) * mag * (1.0 + 0.08 * (1.0 - self._S))
            elif ev.kind == "rumor":
                mag = float(np.clip(ev.magnitude, 0.0, 1.0))
                self._F *= 1.0 - float(self.fulfillment_erosion) * mag

        self._S = float(np.clip(self._S, 0.0, 1.0))
        self._F = float(np.clip(self._F, 0.0, 1.0))

        observation = {
            "reserves": self._S,
            "supply": self._F,
            "panic": float(1.0 - self._S),
            "price": self._S,
            "timestep": self._timestep,
        }
        redeem_fraction = float(np.clip(self.population.aggregate_redeem_fraction(observation, rng), 0.0, 1.0))
        drain = 0.12 * redeem_fraction * (1.0 - self._S)
        self._S = max(0.0, self._S - drain)
        self._S = float(
            np.clip(
                self._S + float(self.replenish_rate) * self._F * (1.0 - min(1.0, 1.0 - self._S)),
                0.0,
                1.0,
            )
        )
        self._F = float(
            np.clip(
                self._F + float(self.stock_recovery) * (self._S - self.stockout_collapse),
                0.0,
                1.0,
            )
        )

        metrics = {
            "price": self._S,
            "backing_ratio": self._F,
            "redeem_fraction": redeem_fraction,
            "paid_out": 0.0,
            "instability": float(self.instability_score()),
        }
        t = self._timestep
        self._timestep += 1
        return TrajectoryStep(
            timestep=t,
            state_vector=self.state_vector(),
            events=events,
            agent_actions_summary={"aggregate_redeem_fraction": redeem_fraction},
            metrics=metrics,
        )
