from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_rollout_is_deterministic():
    world = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=16)
    rng = np.random.default_rng(0)
    genome = rng.uniform(size=(16, 2))
    a = rollout_stablecoin(world, genome, seed=555)
    b = rollout_stablecoin(world, genome, seed=555)
    assert a.collapsed == b.collapsed
    assert len(a.trajectory) == len(b.trajectory)
    for s1, s2 in zip(a.trajectory, b.trajectory, strict=True):
        assert np.allclose(s1.state_vector, s2.state_vector)


def test_extreme_shocks_tend_to_force_failure():
    world = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=24)
    genome = np.ones((24, 2))  # always strongest shocks (bucket maps to rumor / high mag)
    genome[:, 0] = 0.95  # bias toward non-none kinds
    result = rollout_stablecoin(world, genome, seed=1)
    assert result.collapsed is True
