from __future__ import annotations

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution import alternating_coevolution
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
