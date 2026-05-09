"""Phase J scaffold: infrastructure-style overload cascade (non-stablecoin reference domain)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.agents.stablecoin_agents import AgentPopulation
from fragility_engine.types import ExogenousEvent, TrajectoryStep


@dataclass
class ResourceCascadeWorld:
    """
    Two-layer capacity headroom with shared overload stress.

    Interprets the same exogenous **reserve_loss** / **rumor** schedule encoding as the peg toy so
    attacker genomes transfer unchanged; physics is intentionally different (capacity + cascade).
    """

    population: AgentPopulation
    cascade_coupling: float = 0.26
    overload_decay: float = 0.84
    rumor_gain: float = 0.32
    reserve_hit_primary: float = 0.42
    reserve_hit_secondary: float = 0.28
    redeem_damage_primary: float = 0.38
    collapse_headroom: float = 0.09
    recovery_headroom: float = 0.86
    max_steps: int = 40
    _h0: float = 1.0
    _h1: float = 1.0
    _overload: float = 0.0
    _timestep: int = 0

    @property
    def depeg_threshold(self) -> float:
        """Replay recoverability helper — minimum healthy headroom treated like an aggregate price floor."""

        return float(self.recovery_headroom)

    def reset(self, *, initial_overload: float = 0.05, capacity_scale: float = 1.0) -> None:
        """``capacity_scale`` (defender reserve boost ≥ 1) damps initial overload without raising headroom above 1."""

        self._h0 = 1.0
        self._h1 = 1.0
        boost = float(np.clip(capacity_scale, 1.0, 1.5))
        self._overload = float(np.clip(float(initial_overload) / boost, 0.0, 1.0))
        self._timestep = 0

    def state_vector(self) -> np.ndarray:
        return np.array([self._h0, self._h1, self._overload, float(self._timestep)], dtype=np.float64)

    def instability_score(self) -> float:
        head = float(min(self._h0, self._h1))
        return float(0.5 * (2.0 - self._h0 - self._h1) + self._overload + max(0.0, self.recovery_headroom - head))

    def is_collapsed(self) -> bool:
        return bool(min(self._h0, self._h1) < self.collapse_headroom)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        for ev in events:
            if ev.kind == "reserve_loss":
                loss = float(np.clip(ev.magnitude, 0.0, 1.0))
                self._h0 *= 1.0 - self.reserve_hit_primary * loss
                self._h1 *= 1.0 - self.reserve_hit_secondary * loss
            elif ev.kind == "rumor":
                self._overload = float(
                    np.clip(self._overload + self.rumor_gain * float(np.clip(ev.magnitude, 0.0, 1.0)), 0.0, 1.0)
                )

        self._h0 = float(np.clip(self._h0, 0.0, 1.0))
        self._h1 = float(np.clip(self._h1, 0.0, 1.0))

        damp = float(np.clip(1.0 - self.cascade_coupling * (1.0 - self._h0) * self._overload, 0.25, 1.0))
        self._h1 *= damp

        headroom_price = float(min(self._h0, self._h1))
        observation = {
            "reserves": self._h0,
            "supply": 1.0,
            "panic": self._overload,
            "price": headroom_price,
            "timestep": self._timestep,
        }
        redeem_fraction = float(np.clip(self.population.aggregate_redeem_fraction(observation, rng), 0.0, 1.0))
        self._h0 = float(np.clip(self._h0 * (1.0 - self.redeem_damage_primary * redeem_fraction), 0.0, 1.0))

        mean_shortfall = 0.5 * ((1.0 - self._h0) + (1.0 - self._h1))
        self._overload = float(
            np.clip(self._overload * self.overload_decay + 0.05 * mean_shortfall, 0.0, 1.0)
        )

        metrics = {
            "price": headroom_price,
            "backing_ratio": headroom_price,
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
