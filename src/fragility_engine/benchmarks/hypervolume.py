"""Two-objective hypervolume for **minimization** fronts (benchmark / Pareto tooling)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


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


def attack_pareto_to_min_points(
    severity: Sequence[float],
    attack_cost: Sequence[float],
) -> list[tuple[float, float]]:
    """
    Map attack trade-offs to 2-D minimization coordinates.

    Search archives maximize ``severity`` and minimize ``attack_cost``. Standard
    hypervolume assumes both objectives are minimized, so we use ``(-severity, attack_cost)``.
    """

    if len(severity) != len(attack_cost):
        raise ValueError("severity and attack_cost must have the same length")
    return [(-float(s), float(c)) for s, c in zip(severity, attack_cost, strict=True)]


def attack_archive_to_min_points(archive: Sequence[Mapping[str, float]]) -> list[tuple[float, float]]:
    """Extract ``(-severity, attack_cost)`` from ``pareto-front-v1`` archive rows."""

    return attack_pareto_to_min_points(
        [float(row["severity"]) for row in archive],
        [float(row["attack_cost"]) for row in archive],
    )


def default_attack_hypervolume_reference(
    min_points: Sequence[tuple[float, float]],
    *,
    margin_frac: float = 0.15,
    eps: float = 0.01,
) -> tuple[float, float]:
    """
    Reference point strictly worse than all ``min_points`` on both minimized axes.

    Uses ``max + max(|max| * margin_frac, eps)`` per axis so negative ``-severity`` values
    still get a valid dominating reference.
    """

    nd = nondominated_points_min(min_points)
    if not nd:
        raise ValueError("empty nondominated set")
    m1 = max(p[0] for p in nd)
    m2 = max(p[1] for p in nd)
    r1 = m1 + max(abs(m1) * margin_frac, eps)
    r2 = m2 + max(abs(m2) * margin_frac, eps)
    return (float(r1), float(r2))


def hypervolume_2d_attack_pareto(
    archive: Sequence[Mapping[str, float]],
    ref: tuple[float, float] | None = None,
) -> tuple[float, tuple[float, float], list[tuple[float, float]]]:
    """
    Hypervolume of an attack Pareto archive (max severity, min cost).

    Returns ``(hypervolume, reference_used, nondominated_min_points)``.
    """

    min_pts = attack_archive_to_min_points(archive)
    nd = nondominated_points_min(min_pts)
    if not nd:
        return 0.0, ref or (0.0, 0.0), []
    ref_t = ref if ref is not None else default_attack_hypervolume_reference(nd)
    hv = hypervolume_2d_min(nd, ref_t)
    return float(hv), ref_t, nd


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
