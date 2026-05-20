"""Minimal coupled peg + cascade overload (fork research; not main charter)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class CoupledInstitutionWorld:
    """
    Two scalars exchange signals each step: peg panic ``P`` and cascade overload ``O``.

    This is a **toy** coupling contract for fork experiments — not calibrated finance.
    """

    coupling_strength: float = 0.25
    max_steps: int = 20
    _P: float = 0.05
    _O: float = 0.05
    _t: int = 0
    _history: list[dict[str, float]] = field(default_factory=list)

    def reset(self, *, initial_panic: float = 0.05, initial_overload: float = 0.05) -> None:
        self._P = float(initial_panic)
        self._O = float(initial_overload)
        self._t = 0
        self._history = []

    def step_shocks(self, reserve_loss: float = 0.0, rumor: float = 0.0) -> dict[str, float]:
        self._P += 0.4 * reserve_loss + self.coupling_strength * self._O
        self._O += 0.35 * rumor + self.coupling_strength * self._P
        self._P = float(np.clip(self._P, 0.0, 2.0))
        self._O = float(np.clip(self._O, 0.0, 2.0))
        inst = 0.5 * self._P + 0.5 * self._O
        row = {"timestep": float(self._t), "panic": self._P, "overload": self._O, "instability": inst}
        self._history.append(row)
        self._t += 1
        return row

    def collapsed(self) -> bool:
        return bool(self._P >= 1.0 or self._O >= 1.0)


def coupled_rollout_snapshot(*, steps: int = 8, seed: int = 0) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    w = CoupledInstitutionWorld()
    w.reset()
    for _ in range(steps):
        w.step_shocks(reserve_loss=float(rng.uniform(0, 0.3)), rumor=float(rng.uniform(0, 0.2)))
    return {
        "simulation_mode": "coupled_institution_v0",
        "collapsed": w.collapsed(),
        "trajectory": w._history,
        "coupling_strength": w.coupling_strength,
    }
