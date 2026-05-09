from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import crossover_genome, mutate_genome, random_genome
from fragility_engine.adversary.fitness import fitness_phase_a
from fragility_engine.types import RolloutResult, SearchResult


def monte_carlo_search(
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    horizon: int,
    samples: int,
    seed: int,
    fitness_fn: Callable[[RolloutResult], float] | None = None,
) -> SearchResult:
    score = fitness_fn or fitness_phase_a
    rng = np.random.default_rng(seed)
    best_genome = random_genome(horizon, rng)
    best_rollout = rollout_fn(best_genome, seed + 1)
    best_fitness = float(score(best_rollout))

    history: list[dict[str, Any]] = []
    for i in range(samples):
        g = random_genome(horizon, rng)
        r = rollout_fn(g, seed + 2 + i)
        fitness = float(score(r))
        history.append({"sample": i, "fitness": fitness, "collapsed": r.collapsed})
        if fitness > best_fitness:
            best_fitness = fitness
            best_genome = g
            best_rollout = r

    return SearchResult(best_genome=best_genome, best_fitness=best_fitness, best_rollout=best_rollout, history=history)


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
) -> SearchResult:
    score = fitness_fn or fitness_phase_a
    rng = np.random.default_rng(seed)
    population = [random_genome(horizon, rng) for _ in range(population_size)]

    best_fitness = -np.inf
    best_genome = population[0]
    best_rollout = rollout_fn(best_genome, seed + 7)
    best_fitness = float(score(best_rollout))
    history: list[dict[str, Any]] = []

    for gen in range(generations):
        fitnesses: list[float] = []
        rollouts: list[RolloutResult] = []
        for idx, individual in enumerate(population):
            rr = rollout_fn(individual, seed + 1000 + gen * population_size + idx)
            fit = float(score(rr))
            fitnesses.append(fit)
            rollouts.append(rr)
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

    return SearchResult(best_genome=best_genome, best_fitness=best_fitness, best_rollout=best_rollout, history=history)
