"""Plausibility / likelihood axis for stress schedules (AST / Gremlin-inspired).

Scores how far a genome sits from a quiet prior so search can trade severity for
statistical plausibility — without continuous GP priors or MCTS.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import decode_schedule
from fragility_engine.adversary.fitness import severity_score
from fragility_engine.adversary.search import genetic_search, monte_carlo_search
from fragility_engine.types import RolloutResult, SearchResult

PLAUSIBILITY_SEARCH_SCHEMA = "plausibility-search-v1"


def schedule_log_likelihood(
    genome: np.ndarray,
    *,
    mag_sigma: float = 0.35,
    kind_none_logit: float = 1.2,
) -> float:
    """Rough log-density under an independent quiet-ish prior on genome rows.

    - Kind selector prefers the ``none`` bucket (first third of [0,1)).
    - Magnitudes are ~N(0, mag_sigma) folded into [0,1] (higher mag → lower ll).
    Not a calibrated probability — an *insanity* / distance-to-prior proxy.
    """

    if genome.ndim != 2 or genome.shape[1] != 2:
        raise ValueError("Genome must have shape (horizon, 2).")
    g = np.clip(genome.astype(np.float64), 0.0, 1.0)
    ll = 0.0
    sig = max(1e-6, float(mag_sigma))
    for t in range(g.shape[0]):
        sel, mag = float(g[t, 0]), float(g[t, 1])
        # Soft preference for none bucket [0, 1/3)
        in_none = 1.0 if sel < (1.0 / 3.0) else 0.0
        ll += float(kind_none_logit) * in_none - (1.0 - in_none) * 0.5
        # Quadratic penalty on magnitude (quiet prior centered at 0)
        ll += -0.5 * (mag / sig) ** 2
    return float(ll)


def insanity_budget(genome: np.ndarray, *, mag_sigma: float = 0.35) -> float:
    """Non-negative distance from prior: ``-log_likelihood`` shifted to ≥ 0."""

    ll = schedule_log_likelihood(genome, mag_sigma=mag_sigma)
    # Shift so typical quiet schedules are near 0
    return float(max(0.0, -ll))


def fitness_severity_minus_insanity(
    *,
    weight: float,
    mag_sigma: float = 0.35,
    last_genome: dict[str, np.ndarray] | None = None,
) -> Callable[[RolloutResult], float]:
    """Severity minus ``weight * insanity_budget(genome)``.

    ``last_genome`` must be updated by the paired rollout_fn before scoring
    (same pattern as differential search).
    """

    w = float(weight)
    store = last_genome if last_genome is not None else {}

    def _score(r: RolloutResult) -> float:
        g = store.get("genome")
        if g is None:
            return float(severity_score(r))
        return float(severity_score(r) - w * insanity_budget(g, mag_sigma=mag_sigma))

    return _score


@dataclass(frozen=True)
class PlausibilitySearchResult:
    search: SearchResult
    log_likelihood: float
    insanity: float
    plausibility_weight: float


def plausible_search(
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    horizon: int,
    seed: int,
    plausibility_weight: float = 0.35,
    method: str = "ga",
    generations: int = 8,
    population_size: int = 16,
    samples: int = 40,
    mag_sigma: float = 0.35,
) -> PlausibilitySearchResult:
    """GA/MC search with severity − weight × insanity_budget."""

    last: dict[str, np.ndarray] = {}

    def wrapped(genome: np.ndarray, s: int) -> RolloutResult:
        last["genome"] = genome.copy()
        return rollout_fn(genome, s)

    fitness_fn = fitness_severity_minus_insanity(
        weight=plausibility_weight,
        mag_sigma=mag_sigma,
        last_genome=last,
    )
    if method == "mc":
        result = monte_carlo_search(
            wrapped,
            horizon=horizon,
            samples=samples,
            seed=seed,
            fitness_fn=fitness_fn,
        )
    else:
        result = genetic_search(
            wrapped,
            horizon=horizon,
            generations=generations,
            population_size=population_size,
            seed=seed,
            fitness_fn=fitness_fn,
        )
    g = result.best_genome
    ll = schedule_log_likelihood(g, mag_sigma=mag_sigma)
    return PlausibilitySearchResult(
        search=result,
        log_likelihood=ll,
        insanity=insanity_budget(g, mag_sigma=mag_sigma),
        plausibility_weight=float(plausibility_weight),
    )


def plausibility_search_payload(psr: PlausibilitySearchResult) -> dict[str, Any]:
    g = psr.search.best_genome
    r = psr.search.best_rollout
    n_events = sum(len(v) for v in decode_schedule(g).values())
    return {
        "schema": PLAUSIBILITY_SEARCH_SCHEMA,
        "plausibility_weight": psr.plausibility_weight,
        "log_likelihood": psr.log_likelihood,
        "insanity_budget": psr.insanity,
        "best_fitness": psr.search.best_fitness,
        "severity": float(severity_score(r)),
        "attack_cost": float(r.attack_cost),
        "collapsed": bool(r.collapsed),
        "active_shock_events": int(n_events),
        "note": (
            "Insanity budget is −log prior under a quiet independent-row schedule model "
            "(Gremlin-inspired constraint; not a calibrated likelihood)."
        ),
        "genome": g.tolist(),
    }
