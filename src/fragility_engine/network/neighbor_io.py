"""Load list-only graph topology from JSON (no dense adjacency required)."""

from __future__ import annotations

import json
from pathlib import Path


def load_neighbor_topology(
    lists_path: Path,
    weights_path: Path | None = None,
) -> tuple[list[list[int]], list[list[float]] | None]:
    """
    ``lists_path`` JSON: ``[[1,2],[0],...]`` — per-node out-neighbor indices.

    Optional ``weights_path`` JSON: same shape, positive weights per edge.
    """

    raw = json.loads(lists_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("neighbor lists JSON must be a top-level array")
    neighbors: list[list[int]] = []
    for row in raw:
        if not isinstance(row, list):
            raise ValueError("each neighbor row must be an array of ints")
        neighbors.append([int(x) for x in row])

    if weights_path is None:
        return neighbors, None

    wraw = json.loads(weights_path.read_text(encoding="utf-8"))
    if not isinstance(wraw, list) or len(wraw) != len(neighbors):
        raise ValueError("weights JSON row count must match neighbor lists")
    weights: list[list[float]] = []
    for i, row in enumerate(wraw):
        if not isinstance(row, list) or len(row) != len(neighbors[i]):
            raise ValueError(f"weights[{i}] must match neighbors[{i}] length")
        weights.append([float(x) for x in row])
    return neighbors, weights
