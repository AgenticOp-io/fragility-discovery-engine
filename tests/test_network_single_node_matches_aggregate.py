"""
Phase B note: the full graph model is not identical to the aggregate scalar world.

Here we validate the strongest meaningful bridge: **single-node + self-loop** contagion
reduces to local panic dynamics aligned with the aggregate simulator on matching shocks.
"""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin, rollout_stablecoin_network
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_single_node_network_price_track_matches_aggregate_small_horizon():
    pop = default_stablecoin_population()
    agg_template = StablecoinPegWorld(population=pop, max_steps=12)

    net_template = StablecoinNetworkWorld(
        population=pop,
        adjacency=np.ones((1, 1), dtype=np.int8),
        node_weights=np.array([1.0]),
        contagion_beta=0.35,
        panic_decay=agg_template.panic_decay,
        rumor_panic_gain=agg_template.rumor_panic_gain,
        depeg_threshold=agg_template.depeg_threshold,
        max_steps=12,
    )

    genome = np.zeros((12, 2))
    genome[2, 0] = 0.5
    genome[2, 1] = 0.15

    seed = 31415
    ra = rollout_stablecoin(agg_template, genome, seed=seed)
    rn = rollout_stablecoin_network(net_template, genome, seed=seed)

    pa = [float(s.metrics["price"]) for s in ra.trajectory]
    pn = [float(s.metrics["price"]) for s in rn.trajectory]
    assert len(pa) == len(pn)
    np.testing.assert_allclose(pa, pn, rtol=0.0, atol=1e-6)
