"""Phase N — liquidity ladder / margin stress (fourth reference domain, same shock encoding)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.agents.stablecoin_agents import AgentPopulation
from fragility_engine.types import ExogenousEvent, TrajectoryStep


@dataclass
class LiquidityLadderWorld:
    """
    Margin utilization ``M`` and ladder depth ``D`` (funding / collateral runway in ``[0,1]``).

    ``reserve_loss`` shocks raise margin utilization (calls); ``rumor`` shocks erode ladder depth (haircuts).
    Same :class:`~fragility_engine.types.ExogenousEvent` vocabulary as other reference worlds.
    """

    population: AgentPopulation
    margin_call_gain: float = 0.88
    haircut_damage: float = 0.16
    delever_rate: float = 0.34
    depth_recovery: float = 0.05
    margin_collapse: float = 1.12
    depth_floor_collapse: float = 0.12
    recovery_depth: float = 0.78
    max_steps: int = 26
    _M: float = 0.0
    _D: float = 0.93
    _timestep: int = 0

    @property
    def depeg_threshold(self) -> float:
        """Replay recoverability — healthy ladder depth threshold."""

        return float(self.recovery_depth)

    def reset(self, *, initial_margin: float = 0.06, margin_scale: float = 1.0) -> None:
        """``margin_scale`` (defender ``reserve_boost`` ≥ 1) damps initial utilization at reset."""

        boost = float(np.clip(margin_scale, 1.0, 1.5))
        self._M = float(max(0.0, float(initial_margin) / boost))
        self._D = 0.93
        self._timestep = 0

    def state_vector(self) -> np.ndarray:
        mnorm = float(np.clip(self._M / max(self.margin_collapse, 1e-9), 0.0, 1.5))
        return np.array([self._M, self._D, mnorm, float(self._timestep)], dtype=np.float64)

    def instability_score(self) -> float:
        mnorm = self._M / max(self.margin_collapse, 1e-9)
        return float(0.6 * min(mnorm, 2.5) + 0.4 * (1.0 - self._D))

    def is_collapsed(self) -> bool:
        return bool(self._M >= self.margin_collapse or self._D <= self.depth_floor_collapse)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        for ev in events:
            if ev.kind == "reserve_loss":
                mag = float(np.clip(ev.magnitude, 0.0, 1.0))
                self._M += float(self.margin_call_gain) * mag * (1.0 + 0.07 * self._M)
            elif ev.kind == "rumor":
                mag = float(np.clip(ev.magnitude, 0.0, 1.0))
                self._D *= 1.0 - float(self.haircut_damage) * mag

        self._D = float(np.clip(self._D, 0.0, 1.0))

        observation = {
            "reserves": self._D,
            "supply": 1.0,
            "panic": float(np.clip(self._M / max(self.margin_collapse, 1e-9), 0.0, 1.5)),
            "price": self._D,
            "timestep": self._timestep,
        }
        redeem_fraction = float(np.clip(self.population.aggregate_redeem_fraction(observation, rng), 0.0, 1.0))
        self._M = max(
            0.0,
            self._M - float(self.delever_rate) * self._D * (1.0 + 0.18 * redeem_fraction),
        )
        self._D = float(
            np.clip(
                self._D
                + float(self.depth_recovery)
                * (1.0 - min(1.0, self._M / max(self.margin_collapse, 1e-9))),
                0.0,
                1.0,
            )
        )

        headroom = float(self._D)
        metrics = {
            "price": headroom,
            "backing_ratio": headroom,
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
