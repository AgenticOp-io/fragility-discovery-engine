"""Coupled peg panic + cascade overload (fork research; not main charter)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from coupled_institution.types import ExogenousEvent, TrajectoryStep


@dataclass
class CoupledInstitutionWorld:
    """
    Two scalars exchange signals each step: peg panic ``P`` and cascade overload ``O``.

    Toy coupling for fork experiments — not calibrated finance. Implements the same
    shock kinds as main-engine worlds (``reserve_loss``, ``rumor``).
    """

    coupling_strength: float = 0.25
    max_steps: int = 20
    _P: float = 0.05
    _O: float = 0.05
    _t: int = 0

    def reset(self, *, initial_panic: float = 0.05, initial_overload: float = 0.05) -> None:
        self._P = float(initial_panic)
        self._O = float(initial_overload)
        self._t = 0

    def state_vector(self) -> np.ndarray:
        return np.array([self._P, self._O, 0.5 * (self._P + self._O), float(self._t)], dtype=np.float64)

    def instability_score(self) -> float:
        return float(0.5 * self._P + 0.5 * self._O)

    def is_collapsed(self) -> bool:
        return bool(self._P >= 1.0 or self._O >= 1.0)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        reserve_loss = 0.0
        rumor = 0.0
        for ev in events:
            if ev.kind == "reserve_loss":
                reserve_loss += float(np.clip(ev.magnitude, 0.0, 1.0))
            elif ev.kind == "rumor":
                rumor += float(np.clip(ev.magnitude, 0.0, 1.0))

        self._P += 0.4 * reserve_loss + self.coupling_strength * self._O
        self._O += 0.35 * rumor + self.coupling_strength * self._P
        # tiny endogenous noise so identical schedules are not perfectly flat
        self._P += 0.02 * float(rng.normal())
        self._O += 0.02 * float(rng.normal())
        self._P = float(np.clip(self._P, 0.0, 2.0))
        self._O = float(np.clip(self._O, 0.0, 2.0))

        metrics = {
            "price": self._P,
            "backing_ratio": 1.0 - 0.5 * self._O,
            "panic": self._P,
            "overload": self._O,
            "instability": self.instability_score(),
            "coupling_strength": float(self.coupling_strength),
        }
        t = self._t
        self._t += 1
        return TrajectoryStep(
            timestep=t,
            state_vector=self.state_vector(),
            events=events,
            agent_actions_summary={"redeem_fraction": 0.0},
            metrics=metrics,
        )

    # legacy helper used by early scaffold tests
    def step_shocks(self, reserve_loss: float = 0.0, rumor: float = 0.0) -> dict[str, float]:
        events: tuple[ExogenousEvent, ...] = ()
        if reserve_loss > 0:
            events += (ExogenousEvent("reserve_loss", float(reserve_loss)),)
        if rumor > 0:
            events += (ExogenousEvent("rumor", float(rumor)),)
        row = self.step(events, np.random.default_rng(0))
        return {
            "timestep": float(row.timestep),
            "panic": self._P,
            "overload": self._O,
            "instability": float(row.metrics["instability"]),
        }


def coupled_rollout_snapshot(*, steps: int = 8, seed: int = 0) -> dict[str, object]:
    from coupled_institution.rollout import random_schedule, rollout_coupled

    world = CoupledInstitutionWorld()
    sched = random_schedule(steps, seed=seed)
    result = rollout_coupled(world, sched, seed=seed)
    out = result.to_replay_dict()
    out["collapsed"] = result.collapsed
    return out
