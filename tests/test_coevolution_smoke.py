from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution import (
    alternating_coevolution,
    alternating_coevolution_resource_cascade,
    alternating_coevolution_service_backlog,
)
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.service_backlog import ServiceBacklogWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_alternating_coevolution_smoke():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=28)
    summary = alternating_coevolution(
        template,
        attacker_horizon=12,
        defender_genome_size=4,
        rounds=1,
        attacker_generations=2,
        attacker_population=8,
        defender_generations=2,
        defender_population=8,
        seed=707,
    )
    assert summary.best_attacker is not None
    assert summary.best_defender is not None
    assert len(summary.rounds) == 1
    assert summary.last_rollout is not None
    assert len(summary.last_rollout.trajectory) >= 1
    assert summary.last_rollout.simulation_mode == "aggregate"
    assert summary.simulation_mode == "aggregate"


def test_alternating_coevolution_two_rounds_reproducible():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=26)

    def run():
        return alternating_coevolution(
            template,
            attacker_horizon=10,
            defender_genome_size=4,
            rounds=2,
            attacker_generations=2,
            attacker_population=8,
            defender_generations=2,
            defender_population=8,
            seed=919,
        )

    a = run()
    b = run()
    assert len(a.rounds) == len(b.rounds) == 2
    assert a.rounds == b.rounds
    assert np.allclose(a.best_attacker, b.best_attacker)
    assert np.allclose(a.best_defender, b.best_defender)


def test_alternating_coevolution_eval_workers_matches_sequential():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=26)
    kwargs = dict(
        attacker_horizon=10,
        defender_genome_size=4,
        rounds=2,
        attacker_generations=2,
        attacker_population=8,
        defender_generations=2,
        defender_population=8,
        seed=919,
    )
    s1 = alternating_coevolution(template, eval_workers=1, **kwargs)
    s4 = alternating_coevolution(template, eval_workers=4, **kwargs)
    assert s1.rounds == s4.rounds
    assert np.allclose(s1.best_attacker, s4.best_attacker)
    assert np.allclose(s1.best_defender, s4.best_defender)


def test_alternating_coevolution_resource_cascade_eval_workers_matches_sequential():
    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=24)
    kwargs = dict(
        attacker_horizon=8,
        defender_genome_size=4,
        rounds=1,
        attacker_generations=2,
        attacker_population=8,
        defender_generations=2,
        defender_population=7,
        seed=424,
        initial_overload=0.05,
    )
    s1 = alternating_coevolution_resource_cascade(template, eval_workers=1, **kwargs)
    s4 = alternating_coevolution_resource_cascade(template, eval_workers=4, **kwargs)
    assert s1.rounds == s4.rounds
    assert np.allclose(s1.best_attacker, s4.best_attacker)
    assert np.allclose(s1.best_defender, s4.best_defender)


def test_alternating_coevolution_service_backlog_eval_workers_matches_sequential():
    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=24)
    kwargs = dict(
        attacker_horizon=8,
        defender_genome_size=4,
        rounds=1,
        attacker_generations=2,
        attacker_population=8,
        defender_generations=2,
        defender_population=7,
        seed=525,
        initial_backlog=0.05,
    )
    s1 = alternating_coevolution_service_backlog(template, eval_workers=1, **kwargs)
    s4 = alternating_coevolution_service_backlog(template, eval_workers=4, **kwargs)
    assert s1.rounds == s4.rounds
    assert np.allclose(s1.best_attacker, s4.best_attacker)
    assert np.allclose(s1.best_defender, s4.best_defender)
