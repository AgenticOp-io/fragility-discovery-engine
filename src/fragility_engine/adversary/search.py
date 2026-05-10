from __future__ import annotations

import pickle
from collections.abc import Callable
from functools import partial
from typing import Any, Literal

import numpy as np

from fragility_engine.adversary.encoding import crossover_genome, mutate_genome, random_genome
from fragility_engine.adversary.fitness import fitness_phase_a
from fragility_engine.adversary.pareto import ParetoPoint, merge_pareto_points, pareto_point_from_rollout
from fragility_engine.parallel_rollouts import process_pool_map_ordered, thread_pool_map_ordered
from fragility_engine.types import RolloutResult, SearchResult

EvalPool = Literal["threads", "processes"]


def _fitness_rollout_pair(
    pair: tuple[np.ndarray, int],
    *,
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    score: Callable[[RolloutResult], float],
) -> tuple[float, RolloutResult]:
    ind, s = pair
    rr = rollout_fn(ind, s)
    return float(score(rr)), rr


def _ordered_map(
    pool: EvalPool,
    fn: Callable[[tuple[np.ndarray, int]], tuple[float, RolloutResult]],
    pairs: list[tuple[np.ndarray, int]],
    *,
    max_workers: int,
) -> list[tuple[float, RolloutResult]]:
    if max_workers <= 1:
        return [fn(p) for p in pairs]
    if pool == "processes":
        try:
            pickle.dumps(fn)
        except Exception as e:
            raise ValueError(
                "eval_pool='processes' requires a picklable rollout_fn bound for workers "
                "(e.g. functools.partial(fragility_engine.benchmarks.suite.rollout_bundle_with_genome, "
                "<bundle_id>, isolate=True))."
            ) from e
        return list(process_pool_map_ordered(fn, pairs, max_workers=max_workers))
    return list(thread_pool_map_ordered(fn, pairs, max_workers=max_workers))


def monte_carlo_search(
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    horizon: int,
    samples: int,
    seed: int,
    fitness_fn: Callable[[RolloutResult], float] | None = None,
    collect_pareto: bool = False,
    eval_workers: int = 1,
    eval_pool: EvalPool = "threads",
) -> SearchResult:
    score = fitness_fn or fitness_phase_a
    ew = int(eval_workers)
    if ew < 1:
        raise ValueError("eval_workers must be >= 1")
    if eval_pool not in ("threads", "processes"):
        raise ValueError("eval_pool must be 'threads' or 'processes'")
    pool: EvalPool = eval_pool
    rng = np.random.default_rng(seed)
    best_genome = random_genome(horizon, rng)
    best_rollout = rollout_fn(best_genome, seed + 1)
    best_fitness = float(score(best_rollout))

    history: list[dict[str, Any]] = []
    archive: list[ParetoPoint] = []
    if collect_pareto:
        archive.append(pareto_point_from_rollout(best_genome, best_rollout))

    trial_genomes = [random_genome(horizon, rng) for _ in range(samples)]
    pairs: list[tuple[np.ndarray, int]] = [(trial_genomes[i], seed + 2 + i) for i in range(samples)]

    _fn = partial(_fitness_rollout_pair, rollout_fn=rollout_fn, score=score)
    mc_results = _ordered_map(pool, _fn, pairs, max_workers=ew)
    for i in range(samples):
        fitness, r = mc_results[i]
        g = trial_genomes[i]
        history.append({"sample": i, "fitness": fitness, "collapsed": r.collapsed})
        if collect_pareto:
            archive.append(pareto_point_from_rollout(g, r))
        if fitness > best_fitness:
            best_fitness = fitness
            best_genome = g
            best_rollout = r

    pareto_archive = merge_pareto_points(archive) if collect_pareto else []
    return SearchResult(
        best_genome=best_genome,
        best_fitness=best_fitness,
        best_rollout=best_rollout,
        history=history,
        pareto_archive=pareto_archive,
    )


def genetic_search(
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
    collect_pareto: bool = False,
    eval_workers: int = 1,
    eval_pool: EvalPool = "threads",
) -> SearchResult:
    score = fitness_fn or fitness_phase_a
    ew = int(eval_workers)
    if ew < 1:
        raise ValueError("eval_workers must be >= 1")
    if eval_pool not in ("threads", "processes"):
        raise ValueError("eval_pool must be 'threads' or 'processes'")
    pool: EvalPool = eval_pool
    rng = np.random.default_rng(seed)
    population = [random_genome(horizon, rng) for _ in range(population_size)]

    best_rollout = rollout_fn(population[0], seed + 7)
    best_fitness = float(score(best_rollout))
    best_genome = population[0].copy()
    history: list[dict[str, Any]] = []
    archive: list[ParetoPoint] = []
    if collect_pareto:
        archive.append(pareto_point_from_rollout(population[0], best_rollout))

    for gen in range(generations):
        seed_base = seed + 1000 + gen * population_size
        pairs: list[tuple[np.ndarray, int]] = [(population[idx], seed_base + idx) for idx in range(population_size)]

        _fn = partial(_fitness_rollout_pair, rollout_fn=rollout_fn, score=score)
        evaluated = _ordered_map(pool, _fn, pairs, max_workers=ew)
        fitnesses = [e[0] for e in evaluated]
        for idx, (fit, rr) in enumerate(evaluated):
            individual = population[idx]
            if collect_pareto:
                archive.append(pareto_point_from_rollout(individual, rr))
            if fit > best_fitness:
                best_fitness = fit
                best_genome = individual.copy()
                best_rollout = rr

        history.append(
            {
                "generation": gen,
                "mean_fitness": float(np.mean(fitnesses)),
                "max_fitness": float(np.max(fitnesses)),
            }
        )

        elite_n = max(1, int(population_size * elite_frac))
        ranked = sorted(range(population_size), key=lambda i: fitnesses[i], reverse=True)
        elites = [population[i].copy() for i in ranked[:elite_n]]

        next_pop: list[np.ndarray] = elites[:]
        while len(next_pop) < population_size:
            if elite_n >= 2:
                i1, i2 = rng.choice(elite_n, size=2, replace=False)
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

    pareto_archive = merge_pareto_points(archive) if collect_pareto else []
    return SearchResult(
        best_genome=best_genome,
        best_fitness=best_fitness,
        best_rollout=best_rollout,
        history=history,
        pareto_archive=pareto_archive,
    )


def _random_vector(dim: int, rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(size=(dim,))


def _mutate_vector(vec: np.ndarray, rng: np.random.Generator, *, rate: float, sigma: float) -> np.ndarray:
    mask = rng.random(size=vec.shape) < rate
    noise = rng.normal(scale=sigma, size=vec.shape)
    return np.clip(vec + mask * noise, 0.0, 1.0)


def _crossover_vector(a: np.ndarray, b: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    dim = a.shape[0]
    if dim <= 1:
        return a.copy(), b.copy()
    cut = int(rng.integers(1, dim))
    c1 = np.concatenate([a[:cut], b[cut:]])
    c2 = np.concatenate([b[:cut], a[cut:]])
    return c1, c2


def genetic_vector_search(
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    dim: int,
    generations: int,
    population_size: int,
    seed: int,
    elite_frac: float = 0.2,
    mutation_rate: float = 0.28,
    mutation_sigma: float = 0.18,
    fitness_fn: Callable[[RolloutResult], float] | None = None,
    collect_pareto: bool = False,
    eval_workers: int = 1,
    eval_pool: EvalPool = "threads",
) -> SearchResult:
    """Evolutionary search over a bounded ``[0, 1]^{dim}`` defender/policy vector."""

    score = fitness_fn or fitness_phase_a
    ew = int(eval_workers)
    if ew < 1:
        raise ValueError("eval_workers must be >= 1")
    if eval_pool not in ("threads", "processes"):
        raise ValueError("eval_pool must be 'threads' or 'processes'")
    pool: EvalPool = eval_pool
    rng = np.random.default_rng(seed)
    population = [_random_vector(dim, rng) for _ in range(population_size)]

    best_rollout = rollout_fn(population[0], seed + 7)
    best_fitness = float(score(best_rollout))
    best_genome = population[0].copy()
    history: list[dict[str, Any]] = []
    archive: list[ParetoPoint] = []
    if collect_pareto:
        archive.append(pareto_point_from_rollout(population[0], best_rollout))

    for gen in range(generations):
        seed_base = seed + 2000 + gen * population_size
        pairs = [(population[idx], seed_base + idx) for idx in range(population_size)]

        _fn = partial(_fitness_rollout_pair, rollout_fn=rollout_fn, score=score)
        evaluated = _ordered_map(pool, _fn, pairs, max_workers=ew)
        fitnesses = [e[0] for e in evaluated]
        for idx, (fit, rr) in enumerate(evaluated):
            individual = population[idx]
            if collect_pareto:
                archive.append(pareto_point_from_rollout(individual, rr))
            if fit > best_fitness:
                best_fitness = fit
                best_genome = individual.copy()
                best_rollout = rr

        history.append(
            {
                "generation": gen,
                "mean_fitness": float(np.mean(fitnesses)),
                "max_fitness": float(np.max(fitnesses)),
            }
        )

        elite_n = max(1, int(population_size * elite_frac))
        ranked = sorted(range(population_size), key=lambda i: fitnesses[i], reverse=True)
        elites = [population[i].copy() for i in ranked[:elite_n]]

        next_pop: list[np.ndarray] = elites[:]
        while len(next_pop) < population_size:
            if elite_n >= 2:
                i1, i2 = rng.choice(elite_n, size=2, replace=False)
                pa, pb = elites[i1], elites[i2]
            else:
                pa = pb = elites[0]
            c1, c2 = _crossover_vector(pa, pb, rng)
            c1 = _mutate_vector(c1, rng, rate=mutation_rate, sigma=mutation_sigma)
            c2 = _mutate_vector(c2, rng, rate=mutation_rate, sigma=mutation_sigma)
            next_pop.append(c1)
            if len(next_pop) < population_size:
                next_pop.append(c2)

        population = next_pop[:population_size]

    pareto_archive = merge_pareto_points(archive) if collect_pareto else []
    return SearchResult(
        best_genome=best_genome,
        best_fitness=best_fitness,
        best_rollout=best_rollout,
        history=history,
        pareto_archive=pareto_archive,
    )
