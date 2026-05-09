from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from fragility_engine.adversary.fitness import severity_score
from fragility_engine.adversary.search import genetic_search, genetic_vector_search
from fragility_engine.runner import rollout_stablecoin, rollout_stablecoin_network
from fragility_engine.types import RolloutResult, SearchResult
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


@dataclass
class CoevolutionSummary:
    rounds: list[dict[str, Any]] = field(default_factory=list)
    best_attacker: np.ndarray | None = None
    best_defender: np.ndarray | None = None
    last_attacker_search: SearchResult | None = None
    last_defender_search: SearchResult | None = None
    #: Final probe rollout from the last completed round (attacker vs defender); ``None`` if ``rounds==0``.
    last_rollout: RolloutResult | None = None
    simulation_mode: str = "aggregate"


def alternating_coevolution_rollout(
    rollout_fn: Callable[[np.ndarray, int, np.ndarray], RolloutResult],
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
    simulation_mode: str = "aggregate",
) -> CoevolutionSummary:
    """
    Alternating attacker/defender search over an arbitrary rollout closure.

    ``rollout_fn(schedule_genome, seed, defender_genome)`` must be deterministic in ``seed``.
    Use this hook to attach **custom worlds** (larger graphs, different physics) without forking
    the co-evolution loop.
    """

    rng = np.random.default_rng(seed)
    defender = rng.uniform(size=(defender_genome_size,))
    summary = CoevolutionSummary(
        best_defender=defender.copy(),
        simulation_mode=simulation_mode,
    )

    for rd in range(rounds):

        def attacker_rollout(genome: np.ndarray, s: int) -> RolloutResult:
            return rollout_fn(genome, s, defender)

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
            return rollout_fn(attacker, s, dgenome)

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

        probe = rollout_fn(attacker, baseline_seed_offset + rd, defender)
        summary.last_rollout = probe
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


def alternating_coevolution(
    template: StablecoinPegWorld,
    *,
    continue_after_collapse: bool = False,
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
    Lightweight attacker/defender loop on the aggregate peg world:

    - Fix defender ⇒ evolve attacker maximizing severity.
    - Fix attacker ⇒ evolve defender minimizing attacker severity (negative fitness).
    """

    def rollout_fn(g: np.ndarray, s: int, d: np.ndarray) -> RolloutResult:
        return rollout_stablecoin(
            template,
            g,
            seed=s,
            defender_genome=d,
            continue_after_collapse=continue_after_collapse,
        )

    return alternating_coevolution_rollout(
        rollout_fn,
        attacker_horizon=attacker_horizon,
        defender_genome_size=defender_genome_size,
        rounds=rounds,
        attacker_generations=attacker_generations,
        attacker_population=attacker_population,
        defender_generations=defender_generations,
        defender_population=defender_population,
        seed=seed,
        baseline_seed_offset=baseline_seed_offset,
        simulation_mode="aggregate",
    )


def alternating_coevolution_network(
    template: StablecoinNetworkWorld,
    *,
    base_panic: float = 0.05,
    initial_reserves: float = 1_000_000.0,
    initial_supply: float = 1_000_000.0,
    continue_after_collapse: bool = False,
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
    """Same alternating loop on :class:`~fragility_engine.world.stablecoin_network.StablecoinNetworkWorld`."""

    def rollout_fn(g: np.ndarray, s: int, d: np.ndarray) -> RolloutResult:
        return rollout_stablecoin_network(
            template,
            g,
            seed=s,
            defender_genome=d,
            base_panic=base_panic,
            initial_reserves=initial_reserves,
            initial_supply=initial_supply,
            continue_after_collapse=continue_after_collapse,
        )

    return alternating_coevolution_rollout(
        rollout_fn,
        attacker_horizon=attacker_horizon,
        defender_genome_size=defender_genome_size,
        rounds=rounds,
        attacker_generations=attacker_generations,
        attacker_population=attacker_population,
        defender_generations=defender_generations,
        defender_population=defender_population,
        seed=seed,
        baseline_seed_offset=baseline_seed_offset,
        simulation_mode="network",
    )
