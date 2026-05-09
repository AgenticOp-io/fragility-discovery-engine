from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, build_events_lane, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_replay_schema_version_and_events_lane():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=14)
    genome = np.random.default_rng(11).uniform(size=(14, 2))
    r = rollout_stablecoin(template, genome, seed=55)
    d = rollout_to_replay_dict(r)
    assert d["schema_version"] == REPLAY_SCHEMA_VERSION
    assert "events_lane" in d
    assert len(d["events_lane"]) == len(d["trajectory"])
    lane = build_events_lane(r.trajectory)
    assert lane == d["events_lane"]
