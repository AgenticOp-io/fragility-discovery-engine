from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import crossover_genome, mutate_genome, random_genome
from fragility_engine.adversary.fitness import fitness_phase_a
from fragility_engine.adversary.pareto import ParetoPoint, merge_pareto_points, pareto_point_from_rollout
from fragility_engine.types import RolloutResult, SearchResult


def monte_carlo_search(
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    horizon: int,
    samples: int,
    seed: int,
    fitness_fn: Callable[[RolloutResult], float] | None = None,
    collect_pareto: bool = False,
) -> SearchResult:
    score = fitness_fn or fitness_phase_a
    rng = np.random.default_rng(seed)
    best_genome = random_genome(horizon, rng)
    best_rollout = rollout_fn(best_genome, seed + 1)
    best_fitness = float(score(best_rollout))

    history: list[dict[str, Any]] = []
    archive: list[ParetoPoint] = []
    if collect_pareto:
        archive.append(pareto_point_from_rollout(best_genome, best_rollout))

    for i in range(samples):
        g = random_genome(horizon, rng)
        r = rollout_fn(g, seed + 2 + i)
        fitness = float(score(r))
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
) -> SearchResult:
    score = fitness_fn or fitness_phase_a
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
        fitnesses: list[float] = []
        rollouts: list[RolloutResult] = []
        for idx, individual in enumerate(population):
            rr = rollout_fn(individual, seed + 1000 + gen * population_size + idx)
            fit = float(score(rr))
            fitnesses.append(fit)
            rollouts.append(rr)
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
) -> SearchResult:
    """Evolutionary search over a bounded ``[0, 1]^{dim}`` defender/policy vector."""

    score = fitness_fn or fitness_phase_a
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
        fitnesses: list[float] = []
        rollouts: list[RolloutResult] = []
        for idx, individual in enumerate(population):
            rr = rollout_fn(individual, seed + 2000 + gen * population_size + idx)
            fit = float(score(rr))
            fitnesses.append(fit)
            rollouts.append(rr)
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
