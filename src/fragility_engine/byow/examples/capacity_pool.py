"""Tutorial world: bounded capacity pool (surge + leak timing)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from fragility_engine.byow.rollout import run_rollout
from fragility_engine.types import ExogenousEvent, RolloutResult, TrajectoryStep

SIMULATION_MODE = "capacity_pool_example"


@dataclass
class CapacityPoolWorld:
    """Bounded allocation pool under demand surges and allocation leaks."""

    capacity: float = 1.0
    base_demand: float = 0.05
    release_rate: float = 0.25
    base_leak: float = 0.02
    surge_gain: float = 0.50
    leak_gain: float = 0.85
    orphan_ttl: int = 8
    collapse_free_floor: float = 0.05
    denial_collapse: float = 0.35
    max_steps: int = 24

    _active: float = 0.0
    _orphans: list[tuple[int, float]] = field(default_factory=list)
    _denied_last: float = 0.0
    _timestep: int = 0

    def reset(self, *, initial_active: float = 0.15) -> None:
        self._active = float(np.clip(initial_active, 0.0, self.capacity))
        self._orphans = []
        self._denied_last = 0.0
        self._timestep = 0

    def _orphaned_total(self) -> float:
        return float(sum(amount for _, amount in self._orphans))

    def _free(self) -> float:
        return float(max(0.0, self.capacity - self._active - self._orphaned_total()))

    def state_vector(self) -> np.ndarray:
        return np.array(
            [self._active, self._orphaned_total(), self._free(), self._denied_last, float(self._timestep)],
            dtype=np.float64,
        )

    def instability_score(self) -> float:
        utilization = (self._active + self._orphaned_total()) / max(self.capacity, 1e-9)
        denial_pressure = self._denied_last / max(self.base_demand, 1e-9)
        return float(0.6 * min(utilization, 1.0) + 0.4 * min(denial_pressure, 2.5))

    def is_collapsed(self) -> bool:
        return bool(self._free() <= self.collapse_free_floor or self._denied_last >= self.denial_collapse)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        del rng
        surge = 0.0
        leak_frac = self.base_leak
        for ev in events:
            mag = float(np.clip(ev.magnitude, 0.0, 1.0))
            if ev.kind == "reserve_loss":
                surge += self.surge_gain * mag
            elif ev.kind == "rumor":
                leak_frac = min(0.95, leak_frac + self.leak_gain * mag)

        self._orphans = [(t, amt) for (t, amt) in self._orphans if t > self._timestep]

        demand = self.base_demand + surge
        granted = min(demand, self._free())
        self._denied_last = float(demand - granted)
        self._active += granted

        released = self.release_rate * self._active
        self._active -= released
        leaked = leak_frac * released
        if leaked > 1e-12:
            self._orphans.append((self._timestep + self.orphan_ttl, float(leaked)))

        metrics = {
            "free_fraction": self._free() / max(self.capacity, 1e-9),
            "orphaned": self._orphaned_total(),
            "denied": self._denied_last,
            "instability": float(self.instability_score()),
        }
        t = self._timestep
        self._timestep += 1
        return TrajectoryStep(
            timestep=t,
            state_vector=self.state_vector(),
            events=events,
            agent_actions_summary={},
            metrics=metrics,
        )


def make_world() -> CapacityPoolWorld:
    return CapacityPoolWorld()


def rollout(world: CapacityPoolWorld, genome: np.ndarray, seed: int) -> RolloutResult:
    return run_rollout(
        world,
        genome,
        seed=seed,
        simulation_mode=SIMULATION_MODE,
        reset=lambda: world.reset(initial_active=0.15),
    )
