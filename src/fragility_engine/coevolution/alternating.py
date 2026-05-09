from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from fragility_engine.adversary.fitness import severity_score
from fragility_engine.adversary.search import genetic_search, genetic_vector_search
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.types import RolloutResult, SearchResult
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


@dataclass
class CoevolutionSummary:
    rounds: list[dict[str, Any]] = field(default_factory=list)
    best_attacker: np.ndarray | None = None
    best_defender: np.ndarray | None = None
    last_attacker_search: SearchResult | None = None
    last_defender_search: SearchResult | None = None


def alternating_coevolution(
    template: StablecoinPegWorld,
    *,
    attacker_horizon: int = 20,
    defender_genome_size: int = 4,
    rounds: int = 3,
    attacker_generations: int = 8,
    attacker_population: int = 18,
    defender_generations: int = 8,
    defender_population: int = 16,
    seed: int = 4242,
    baseline_seed_offset: int = 50_000,
) -> CoevolutionSummary:
    """
    Lightweight attacker/defender loop:

    - Fix defender ⇒ evolve attacker maximizing severity.
    - Fix attacker ⇒ evolve defender minimizing attacker severity (negative fitness).
    """

    rng = np.random.default_rng(seed)
    defender = rng.uniform(size=(defender_genome_size,))
    summary = CoevolutionSummary(best_defender=defender.copy())

    for rd in range(rounds):

        def attacker_rollout(genome: np.ndarray, s: int) -> RolloutResult:
            return rollout_stablecoin(
                template,
                genome,
                seed=s,
                defender_genome=defender,
            )

        att_search = genetic_search(
            attacker_rollout,
            horizon=attacker_horizon,
            generations=attacker_generations,
            population_size=attacker_population,
            seed=seed + rd * 997 + 3,
        )
        attacker = att_search.best_genome.copy()
        summary.best_attacker = attacker
        summary.last_attacker_search = att_search

        def defender_rollout(dgenome: np.ndarray, s: int) -> RolloutResult:
            return rollout_stablecoin(
                template,
                attacker,
                seed=s,
                defender_genome=dgenome,
            )

        def defender_fitness(r: RolloutResult) -> float:
            return -float(severity_score(r))

        def_search = genetic_vector_search(
            defender_rollout,
            dim=defender_genome_size,
            generations=defender_generations,
            population_size=defender_population,
            seed=seed + rd * 991 + 9,
            fitness_fn=defender_fitness,
        )
        defender = def_search.best_genome.copy()
        summary.best_defender = defender.copy()
        summary.last_defender_search = def_search

        probe = rollout_stablecoin(
            template,
            attacker,
            seed=baseline_seed_offset + rd,
            defender_genome=defender,
        )
        summary.rounds.append(
            {
                "round": rd,
                "severity": float(severity_score(probe)),
                "collapsed": probe.collapsed,
                "attack_cost": probe.attack_cost,
                "integral_instability": probe.integral_instability,
            }
        )

    return summary
