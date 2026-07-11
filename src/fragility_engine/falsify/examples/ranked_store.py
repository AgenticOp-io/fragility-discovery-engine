"""Falsification example: ranked retrieval where stale must not surface."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from fragility_engine.falsify.protocol import SnapshotMixin
from fragility_engine.falsify.rollout import run_falsification_rollout
from fragility_engine.types import ExogenousEvent, RolloutResult, TrajectoryStep

SIMULATION_MODE = "falsification_ranked_store_v1"


@dataclass
class RankedStoreWorld(SnapshotMixin):
    """
    Tiny ranked key-value store. Invariant: no **stale** record appears in top-k.

    ``reserve_loss`` injects a high-scoring record; ``rumor`` ages/boosts stale entries.
    """

    top_k: int = 3
    stale_after: int = 4
    max_steps: int = 18

    _records: dict[str, tuple[float, int]] = field(default_factory=dict)
    _timestep: int = 0
    _snapshot: dict | None = field(default=None, repr=False)

    def reset(self) -> None:
        self._records = {
            "fresh_alpha": (1.0, 0),
            "fresh_beta": (0.85, 0),
            "fresh_gamma": (0.7, 0),
        }
        self._timestep = 0
        self.save_snapshot()

    def _snapshot_payload(self) -> dict:
        return {"records": dict(self._records), "timestep": self._timestep}

    def _restore_snapshot_payload(self, snap: dict) -> None:
        self._records = dict(snap["records"])
        self._timestep = int(snap["timestep"])

    def _ranked_ids(self) -> list[str]:
        return sorted(self._records, key=lambda k: self._records[k][0], reverse=True)[: self.top_k]

    def _is_stale(self, doc_id: str) -> bool:
        _score, birth = self._records[doc_id]
        return (self._timestep - birth) > self.stale_after

    def claim_violated(self) -> bool:
        return any(self._is_stale(doc_id) for doc_id in self._ranked_ids())

    def is_collapsed(self) -> bool:
        return self.claim_violated()

    def state_vector(self) -> np.ndarray:
        stale_in_top = sum(1 for doc_id in self._ranked_ids() if self._is_stale(doc_id))
        return np.array([float(stale_in_top), float(len(self._records)), float(self._timestep)], dtype=np.float64)

    def instability_score(self) -> float:
        stale_in_top = sum(1 for doc_id in self._ranked_ids() if self._is_stale(doc_id))
        return float(stale_in_top)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        del rng
        for ev in events:
            mag = float(np.clip(ev.magnitude, 0.0, 1.0))
            if ev.kind == "reserve_loss":
                new_id = f"inj_{self._timestep}_{len(self._records)}"
                self._records[new_id] = (0.5 + 0.5 * mag, self._timestep)
            elif ev.kind == "rumor":
                for doc_id in list(self._records):
                    score, birth = self._records[doc_id]
                    age_boost = 0.15 * mag if (self._timestep - birth) > 0 else 0.0
                    self._records[doc_id] = (score + age_boost + 0.25 * mag, birth)

        metrics = {
            "stale_in_top_k": float(sum(1 for d in self._ranked_ids() if self._is_stale(d))),
            "instability": float(self.instability_score()),
        }
        t = self._timestep
        self._timestep += 1
        return TrajectoryStep(
            timestep=t,
            state_vector=self.state_vector(),
            events=events,
            agent_actions_summary={"top_k": list(self._ranked_ids())},
            metrics=metrics,
        )


def make_world() -> RankedStoreWorld:
    return RankedStoreWorld()


def rollout(world: RankedStoreWorld, genome: np.ndarray, seed: int) -> RolloutResult:
    return run_falsification_rollout(world, genome, seed=seed, simulation_mode=SIMULATION_MODE)
