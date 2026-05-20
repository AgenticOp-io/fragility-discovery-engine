"""Phase O stretch presets for robustness sweeps (larger grids with rollout caps)."""

from __future__ import annotations

from typing import Any

STRETCH_PRESETS: dict[str, dict[str, Any]] = {
    "small": {
        "graph_seeds": "101,102,103,104",
        "ga_generations_values": "2,3,4",
        "ga_population_values": "8,12",
        "max_rollout_budget": 48,
    },
    "medium": {
        "graph_seeds": "101,102,103,104,105,106",
        "sweep_values": "0.08,0.12,0.16,0.20",
        "sweep_values_2": "0.10,0.14,0.18",
        "ga_generations_values": "2,4,6",
        "ga_population_values": "8,12,16",
        "max_rollout_budget": 120,
    },
    "large": {
        "graph_seeds": "101,102,103,104,105,106,107,108",
        "sweep_values": "0.06,0.10,0.14,0.18,0.22",
        "sweep_values_2": "0.08,0.12,0.16,0.20,0.24",
        "ga_generations_values": "2,4,6,8",
        "ga_population_values": "8,12,16,20",
        "max_rollout_budget": 256,
    },
}


def estimate_rollout_budget(preset: dict[str, Any], *, mode: str) -> int:
    """Rough upper bound on inner rollouts for logging (not exact GA cost)."""

    seeds = len(str(preset.get("graph_seeds", "101")).split(","))
    if mode == "ga_budget_2d":
        g = len(str(preset.get("ga_generations_values", "2")).split(","))
        p = len(str(preset.get("ga_population_values", "8")).split(","))
        return seeds * g * p * 4
    if mode == "physics_2d":
        vx = len(str(preset.get("sweep_values", "0.1")).split(","))
        vy = len(str(preset.get("sweep_values_2", "0.1")).split(","))
        return seeds * vx * vy
    return seeds * 4
