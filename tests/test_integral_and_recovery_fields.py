from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_integral_instability_accumulates():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=16)
    genome = np.zeros((16, 2))
    r = rollout_stablecoin(template, genome, seed=44)
    assert r.integral_instability >= 0.0
    assert len(r.trajectory) > 0


def test_continue_after_collapse_flag_runs_longer_when_collapsed():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=24)
    genome = np.ones((24, 2))
    genome[:, 0] = 0.95
    r_fast = rollout_stablecoin(template, genome, seed=8, continue_after_collapse=False)
    r_full = rollout_stablecoin(template, genome, seed=8, continue_after_collapse=True)
    assert len(r_full.trajectory) >= len(r_fast.trajectory)
