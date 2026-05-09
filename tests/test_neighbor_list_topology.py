"""List-only topology + optional directed edge weights."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.defender import build_defended_network_world
from fragility_engine.network.contagion import neighbor_average_panic_lists
from fragility_engine.network.neighbor_io import load_neighbor_topology
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_load_neighbor_topology_roundtrip(tmp_path: Path) -> None:
    nl = [[1, 2], [0], [0]]
    p = tmp_path / "n.json"
    p.write_text(json.dumps(nl), encoding="utf-8")
    loaded, w = load_neighbor_topology(p)
    assert loaded == nl
    assert w is None


def test_load_neighbor_topology_with_weights(tmp_path: Path) -> None:
    nl = [[1], [0]]
    w = [[2.0], [3.0]]
    p1 = tmp_path / "n.json"
    p2 = tmp_path / "w.json"
    p1.write_text(json.dumps(nl), encoding="utf-8")
    p2.write_text(json.dumps(w), encoding="utf-8")
    ln, lw = load_neighbor_topology(p1, p2)
    assert ln == nl
    assert lw == w


def test_neighbor_average_weighted_is_convex_combo() -> None:
    panic = np.array([0.1, 0.9, 0.5], dtype=np.float64)
    neighbors = [[1, 2]]
    weights = [[1.0, 3.0]]
    got = neighbor_average_panic_lists(panic, neighbors, weights=weights)
    expected = (1.0 * 0.9 + 3.0 * 0.5) / 4.0
    assert abs(got[0] - expected) < 1e-12


def test_stablecoin_network_list_only_rollout_smoke() -> None:
    nl = [[1], [0]]
    w = default_whale_weights(2, whale_index=0, whale_frac=0.3)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=w,
        contagion_beta=0.3,
        max_steps=12,
    )
    genome = np.zeros((6, 2), dtype=np.float64)
    r = rollout_stablecoin_network(template, genome, seed=9001)
    assert r.simulation_mode == "network"
    assert len(r.trajectory) >= 1


def test_build_defended_network_world_clones_neighbor_lists() -> None:
    nl = [[1], [0]]
    w = default_whale_weights(2, whale_index=0, whale_frac=0.25)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        neighbor_weights=[[1.0], [2.0]],
        node_weights=w,
        max_steps=10,
    )
    defended, boost = build_defended_network_world(template, np.array([0.5, 0.5, 0.5, 0.5]))
    assert boost >= 1.0
    assert defended.adjacency is None
    assert defended._neighbor_lists == nl
    assert defended._neighbor_weights is not None


@pytest.mark.parametrize("both_or_none", [True, False])
def test_stablecoin_network_rejects_adjacency_and_lists_together(both_or_none: bool) -> None:
    adj = np.array([[0, 1], [1, 0]], dtype=np.int8)
    nl = [[1], [0]]
    with pytest.raises(ValueError, match="exactly one"):
        if both_or_none:
            StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                adjacency=adj,
                neighbor_lists=nl,
                node_weights=np.ones(2),
            )
        else:
            StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                node_weights=np.ones(2),
            )
