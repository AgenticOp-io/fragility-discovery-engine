"""Merge co-evolution ``attacker_pareto`` entries into ``pareto-front-v1`` JSON."""

from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.adversary.pareto import ParetoPoint, merge_pareto_points


def flatten_coevolution_attacker_pareto(rounds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect ``round["attacker_pareto"]`` dicts from alternating co-evolution summary rounds."""

    out: list[dict[str, Any]] = []
    for rd in rounds:
        arch = rd.get("attacker_pareto")
        if isinstance(arch, list):
            for item in arch:
                if isinstance(item, dict):
                    out.append(item)
    return out


def pareto_front_payload_from_archive_dicts(
    entries: list[dict[str, Any]],
    *,
    best_fitness: float | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    """
    Build JSON compatible with ``artifacts/pareto_viewer`` and ``export_pareto_front.py``.

    Entries lack genomes (co-evolution archives metrics only); emitted ``genome`` is ``[]``.
    """

    if not entries:
        raise ValueError("entries must be non-empty")

    points: list[ParetoPoint] = []
    for d in entries:
        points.append(
            ParetoPoint(
                genome=np.zeros((0, 2), dtype=np.float64),
                severity=float(d["severity"]),
                attack_cost=float(d["attack_cost"]),
                collapsed=bool(d.get("collapsed", False)),
                integral_instability=float(d.get("integral_instability", 0.0)),
            )
        )
    merged = merge_pareto_points(points)
    payload: dict[str, Any] = {
        "schema": "pareto-front-v1",
        "archive": [
            {
                "severity": p.severity,
                "attack_cost": p.attack_cost,
                "collapsed": p.collapsed,
                "integral_instability": p.integral_instability,
                "genome": p.genome.tolist(),
            }
            for p in merged
        ],
    }
    if best_fitness is not None:
        payload["best_fitness"] = float(best_fitness)
    if source is not None:
        payload["source"] = source
    return payload
