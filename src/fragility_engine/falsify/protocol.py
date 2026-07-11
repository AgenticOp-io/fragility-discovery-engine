"""Falsification harness: predicate collapse + snapshot reset (Phase S)."""

from __future__ import annotations

import copy
from typing import Any, Protocol

from fragility_engine.types import ExogenousEvent, TrajectoryStep

HARNESS_KIND = "falsification_v1"


class FalsificationWorldProtocol(Protocol):
    """World that reports damage as an invariant predicate (claim violated)."""

    max_steps: int

    def reset(self) -> None: ...

    def save_snapshot(self) -> None: ...

    def restore_snapshot(self) -> None: ...

    def step(self, events: tuple[ExogenousEvent, ...], rng: Any) -> TrajectoryStep: ...

    def state_vector(self) -> Any: ...

    def instability_score(self) -> float: ...

    def is_collapsed(self) -> bool: ...

    def claim_violated(self) -> bool: ...


class SnapshotMixin:
    """Copy-on-save / restore for in-memory world state."""

    def save_snapshot(self) -> None:
        self._snapshot = copy.deepcopy(self._snapshot_payload())  # type: ignore[attr-defined]

    def restore_snapshot(self) -> None:
        snap = getattr(self, "_snapshot", None)
        if snap is None:
            raise RuntimeError("No snapshot saved; call save_snapshot() after reset().")
        self._restore_snapshot_payload(snap)  # type: ignore[attr-defined]
