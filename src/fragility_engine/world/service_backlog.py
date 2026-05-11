"""Phase M — service backlog / latency stress (third reference domain, same shock encoding)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.agents.stablecoin_agents import AgentPopulation
from fragility_engine.types import ExogenousEvent, TrajectoryStep


@dataclass
class ServiceBacklogWorld:
    """
    Work backlog ``B`` and service slack ``S`` (capacity headroom in ``[0,1]``).

    ``reserve_loss`` shocks add inbound load; ``rumor`` shocks erode slack (pressure / staffing / trust).
    Same :class:`~fragility_engine.types.ExogenousEvent` vocabulary as peg + cascade worlds.
    """

    population: AgentPopulation
    ingest_gain: float = 0.95
    rumor_slack_damage: float = 0.14
    process_rate: float = 0.38
    slack_recovery: float = 0.04
    backlog_collapse: float = 5.0
    slack_floor_collapse: float = 0.11
    recovery_slack: float = 0.8
    max_steps: int = 26
    _B: float = 0.0
    _S: float = 0.95
    _timestep: int = 0

    @property
    def depeg_threshold(self) -> float:
        """Replay recoverability — treat healthy slack like a “re-peg” threshold."""

        return float(self.recovery_slack)

    def reset(self, *, initial_backlog: float = 0.05, backlog_scale: float = 1.0) -> None:
        """``backlog_scale`` (defender ``reserve_boost`` ≥ 1) damps initial backlog."""

        boost = float(np.clip(backlog_scale, 1.0, 1.5))
        self._B = float(max(0.0, float(initial_backlog) / boost))
        self._S = 0.95
        self._timestep = 0

    def state_vector(self) -> np.ndarray:
        nb = float(np.clip(self._B / max(self.backlog_collapse, 1e-9), 0.0, 1.0))
        return np.array([self._B, self._S, nb, float(self._timestep)], dtype=np.float64)

    def instability_score(self) -> float:
        bnorm = self._B / max(self.backlog_collapse, 1e-9)
        return float(0.55 * min(bnorm, 2.5) + 0.45 * (1.0 - self._S))

    def is_collapsed(self) -> bool:
        return bool(self._B >= self.backlog_collapse or self._S <= self.slack_floor_collapse)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        for ev in events:
            if ev.kind == "reserve_loss":
                mag = float(np.clip(ev.magnitude, 0.0, 1.0))
                self._B += float(self.ingest_gain) * mag * (1.0 + 0.06 * self._B)
            elif ev.kind == "rumor":
                mag = float(np.clip(ev.magnitude, 0.0, 1.0))
                self._S *= 1.0 - float(self.rumor_slack_damage) * mag

        self._S = float(np.clip(self._S, 0.0, 1.0))

        observation = {
            "reserves": self._S,
            "supply": 1.0,
            "panic": float(np.clip(self._B / max(self.backlog_collapse, 1e-9), 0.0, 1.0)),
            "price": self._S,
            "timestep": self._timestep,
        }
        redeem_fraction = float(np.clip(self.population.aggregate_redeem_fraction(observation, rng), 0.0, 1.0))
        self._B = max(0.0, self._B - float(self.process_rate) * self._S * (1.0 + 0.2 * redeem_fraction))
        self._S = float(
            np.clip(
                self._S + float(self.slack_recovery) * (1.0 - min(1.0, self._B / max(self.backlog_collapse, 1e-9))),
                0.0,
                1.0,
            )
        )

        headroom = float(self._S)
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
