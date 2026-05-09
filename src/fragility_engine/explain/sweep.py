"""Deterministic ε-style sweeps over scalar network physics (Phase I backlog)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np

from fragility_engine.coevolution.defender import clone_stablecoin_network
from fragility_engine.explain.counterfactual import rollout_snapshot
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld

SweepAxis = Literal["base_panic", "contagion_beta"]

SCHEMA = "counterfactual-epsilon-sweep-v1"


def sweep_network_scalar_axis(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    axis: SweepAxis,
    values: list[float],
    rollout_seed: int,
    fixed_base_panic: float | None = None,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """
    Same genome and rollout seed; vary one scalar axis holding topology fixed.

    For ``contagion_beta``, ``fixed_base_panic`` must be set (panic at reset).
    For ``base_panic``, ``fixed_base_panic`` is ignored.
    """

    if not values:
        raise ValueError("values must be non-empty")

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    if axis == "base_panic":
        for v in values:
            bp = float(v)
            r = rollout_stablecoin_network(
                template,
                genome,
                seed=int(rollout_seed),
                base_panic=bp,
                continue_after_collapse=bool(continue_after_collapse),
            )
            integrals.append(float(r.integral_instability))
            row = {"base_panic": bp, **rollout_snapshot(r)}
            runs.append(row)
    else:
        if fixed_base_panic is None:
            raise ValueError("fixed_base_panic required for contagion_beta sweep")
        bp = float(fixed_base_panic)
        for v in values:
            b = float(v)
            tw = clone_stablecoin_network(template, contagion_beta=b)
            r = rollout_stablecoin_network(
                tw,
                genome,
                seed=int(rollout_seed),
                base_panic=bp,
                continue_after_collapse=bool(continue_after_collapse),
            )
            integrals.append(float(r.integral_instability))
            row = {"contagion_beta": b, **rollout_snapshot(r)}
            runs.append(row)

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": axis,
        "rollout_seed": int(rollout_seed),
        "runs": runs,
        "summary": summary,
    }
