"""Two-objective hypervolume for **minimization** fronts (benchmark / Pareto tooling)."""

from __future__ import annotations

from collections.abc import Sequence


def nondominated_points_min(
    points: Sequence[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Return the non-dominated subset for two **minimized** objectives (lower is better)."""

    pts = [(float(a), float(b)) for a, b in points]
    out: list[tuple[float, float]] = []
    for i, p in enumerate(pts):
        dominated = False
        for j, q in enumerate(pts):
            if i == j:
                continue
            if q[0] <= p[0] and q[1] <= p[1] and (q[0] < p[0] or q[1] < p[1]):
                dominated = True
                break
        if not dominated:
            out.append(p)
    return out


def hypervolume_2d_min(points: Sequence[tuple[float, float]], ref: tuple[float, float]) -> float:
    """
    Hypervolume of a **minimization** 2-D front w.r.t. reference point ``ref``.

    ``ref = (r1, r2)`` must **strictly dominate** the ideal point (both coordinates strictly
    worse / **larger** than any objective value realized on the non-dominated set). The dominated
    region is the union of axis-aligned rectangles from each front point up to ``ref``.
    """

    r1, r2 = float(ref[0]), float(ref[1])
    nd = nondominated_points_min(points)
    if not nd:
        return 0.0
    nd.sort(key=lambda p: p[0])
    for x, y in nd:
        if x >= r1 or y >= r2:
            raise ValueError(f"reference must strictly dominate all points; got point ({x}, {y}) vs ref ({r1}, {r2})")
    total = 0.0
    prev_x = r1
    for i in range(len(nd) - 1, -1, -1):
        x, y = nd[i]
        width = prev_x - x
        total += width * (r2 - y)
        prev_x = x
    return float(total)
