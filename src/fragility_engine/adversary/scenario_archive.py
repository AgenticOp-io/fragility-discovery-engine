"""Quality-diversity (MAP-Elites–style) scenario archive for stress search.

Illuminates a grid of behavior descriptors while keeping the highest-severity
elite per niche. Complements ``pareto-front-v1`` (severity vs cost trade-off)
with coverage of *kinds* of failures.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import crossover_genome, mutate_genome, random_genome
from fragility_engine.adversary.fitness import fitness_phase_a, severity_score
from fragility_engine.adversary.search import EvalPool, _fitness_rollout_pair, _ordered_map
from fragility_engine.types import RolloutResult, SearchResult

SCENARIO_ARCHIVE_SCHEMA = "scenario-archive-v1"
DEFAULT_BEHAVIOR_AXES = ("collapse_bin", "severity_bin", "cost_bin")


@dataclass(frozen=True)
class ScenarioElite:
    genome: np.ndarray
    severity: float
    attack_cost: float
    collapsed: bool
    integral_instability: float
    collapse_timestep: int | None
    behavior_descriptor: tuple[int, ...]
    niche_key: str


@dataclass
class QualityDiversityResult:
    """QD search output: best-by-fitness plus illuminated niche archive."""

    search: SearchResult
    niches: dict[str, ScenarioElite] = field(default_factory=dict)
    behavior_axes: tuple[str, ...] = DEFAULT_BEHAVIOR_AXES
    grid_shape: tuple[int, ...] = (4, 5, 5)


def behavior_descriptor(
    rollout: RolloutResult,
    *,
    horizon: int,
    severity_bins: int = 5,
    cost_bins: int = 5,
    severity_max: float = 20.0,
    cost_max: float = 10.0,
) -> tuple[int, int, int]:
    """Map a rollout to discrete niche indices ``(collapse_bin, severity_bin, cost_bin)``."""

    h = max(1, int(horizon))
    if not rollout.collapsed or rollout.collapse_timestep is None:
        collapse_bin = 0
    else:
        # 0 = no collapse; 1..3 = early / mid / late within horizon
        frac = float(rollout.collapse_timestep) / float(h)
        collapse_bin = 1 if frac < 0.34 else (2 if frac < 0.67 else 3)

    sev = float(severity_score(rollout))
    sev_bin = int(np.clip(np.floor(sev / severity_max * severity_bins), 0, severity_bins - 1))
    cost = float(rollout.attack_cost)
    cost_bin = int(np.clip(np.floor(cost / cost_max * cost_bins), 0, cost_bins - 1))
    return (collapse_bin, sev_bin, cost_bin)


def niche_key(descriptor: tuple[int, ...]) -> str:
    return "x".join(str(i) for i in descriptor)


def elite_from_rollout(genome: np.ndarray, rollout: RolloutResult, *, horizon: int) -> ScenarioElite:
    bd = behavior_descriptor(rollout, horizon=horizon)
    return ScenarioElite(
        genome=genome.copy(),
        severity=float(severity_score(rollout)),
        attack_cost=float(rollout.attack_cost),
        collapsed=bool(rollout.collapsed),
        integral_instability=float(rollout.integral_instability),
        collapse_timestep=rollout.collapse_timestep,
        behavior_descriptor=bd,
        niche_key=niche_key(bd),
    )


def _consider(niches: dict[str, ScenarioElite], elite: ScenarioElite) -> None:
    cur = niches.get(elite.niche_key)
    if cur is None or elite.severity > cur.severity:
        niches[elite.niche_key] = elite


def quality_diversity_search(
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    horizon: int,
    generations: int,
    population_size: int,
    seed: int,
    elite_frac: float = 0.2,
    mutation_rate: float = 0.18,
    mutation_sigma: float = 0.14,
    fitness_fn: Callable[[RolloutResult], float] | None = None,
    eval_workers: int = 1,
    eval_pool: EvalPool = "threads",
) -> QualityDiversityResult:
    """GA that also maintains a MAP-Elites–style niche archive (max severity per cell)."""

    score = fitness_fn or fitness_phase_a
    ew = int(eval_workers)
    if ew < 1:
        raise ValueError("eval_workers must be >= 1")
    if eval_pool not in ("threads", "processes"):
        raise ValueError("eval_pool must be 'threads' or 'processes'")
    pool: EvalPool = eval_pool
    rng = np.random.default_rng(seed)
    population = [random_genome(horizon, rng) for _ in range(population_size)]
    niches: dict[str, ScenarioElite] = {}

    best_rollout = rollout_fn(population[0], seed + 7)
    best_fitness = float(score(best_rollout))
    best_genome = population[0].copy()
    history: list[dict[str, Any]] = []
    _consider(niches, elite_from_rollout(population[0], best_rollout, horizon=horizon))

    for gen in range(generations):
        seed_base = seed + 1000 + gen * population_size
        pairs = [(population[idx], seed_base + idx) for idx in range(population_size)]
        _fn = partial(_fitness_rollout_pair, rollout_fn=rollout_fn, score=score)
        evaluated = _ordered_map(pool, _fn, pairs, max_workers=ew)
        fitnesses = [e[0] for e in evaluated]
        for idx, (fit, rr) in enumerate(evaluated):
            individual = population[idx]
            _consider(niches, elite_from_rollout(individual, rr, horizon=horizon))
            if fit > best_fitness:
                best_fitness = fit
                best_genome = individual.copy()
                best_rollout = rr

        history.append(
            {
                "generation": gen,
                "mean_fitness": float(np.mean(fitnesses)),
                "max_fitness": float(np.max(fitnesses)),
                "niche_count": len(niches),
            }
        )

        elite_n = max(1, int(population_size * elite_frac))
        ranked = sorted(range(population_size), key=lambda i: fitnesses[i], reverse=True)
        elites = [population[i].copy() for i in ranked[:elite_n]]
        # Inject archive elites into mating pool for illumination pressure
        archive_list = list(niches.values())
        if archive_list:
            take = min(len(archive_list), max(1, elite_n // 2))
            picks = rng.choice(len(archive_list), size=take, replace=False)
            if np.isscalar(picks):
                picks = [int(picks)]
            else:
                picks = [int(i) for i in picks]
            elites = elites[: max(1, elite_n - take)] + [archive_list[i].genome.copy() for i in picks]

        next_pop: list[np.ndarray] = elites[:]
        while len(next_pop) < population_size:
            if len(elites) >= 2:
                i1, i2 = rng.choice(len(elites), size=2, replace=False)
                parent_a, parent_b = elites[i1], elites[i2]
            else:
                parent_a = parent_b = elites[0]
            c1, c2 = crossover_genome(parent_a, parent_b, rng)
            c1 = mutate_genome(c1, rng, rate=mutation_rate, sigma=mutation_sigma)
            c2 = mutate_genome(c2, rng, rate=mutation_rate, sigma=mutation_sigma)
            next_pop.append(c1)
            if len(next_pop) < population_size:
                next_pop.append(c2)
        population = next_pop[:population_size]

    search = SearchResult(
        best_genome=best_genome,
        best_fitness=best_fitness,
        best_rollout=best_rollout,
        history=history,
        pareto_archive=[],
    )
    return QualityDiversityResult(
        search=search,
        niches=niches,
        behavior_axes=DEFAULT_BEHAVIOR_AXES,
        grid_shape=(4, 5, 5),
    )


def scenario_archive_payload(qd: QualityDiversityResult) -> dict[str, Any]:
    """Serialize niches to ``scenario-archive-v1`` JSON."""

    niches_out: list[dict[str, Any]] = []
    for key in sorted(qd.niches):
        e = qd.niches[key]
        niches_out.append(
            {
                "niche_key": e.niche_key,
                "behavior_descriptor": list(e.behavior_descriptor),
                "severity": e.severity,
                "attack_cost": e.attack_cost,
                "collapsed": e.collapsed,
                "integral_instability": e.integral_instability,
                "collapse_timestep": e.collapse_timestep,
                "genome": e.genome.tolist(),
            }
        )
    return {
        "schema": SCENARIO_ARCHIVE_SCHEMA,
        "behavior_axes": list(qd.behavior_axes),
        "grid_shape": list(qd.grid_shape),
        "niche_count": len(niches_out),
        "best_fitness": qd.search.best_fitness,
        "niches": niches_out,
    }
