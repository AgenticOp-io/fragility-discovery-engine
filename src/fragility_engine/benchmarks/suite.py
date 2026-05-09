"""Frozen deterministic bundles for reproducibility regression (Phase H)."""

from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import rollout_stablecoin, rollout_stablecoin_network
from fragility_engine.types import RolloutResult
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld

RESULT_SCHEMA = "benchmark-bundle-result-v1"

# Pin genome + rollout seed so CI matches local; tolerances in tests absorb tiny FP drift.
_GENOME_SEED = 9001
_ROLLOUT_SEED = 4242
_GENOME_ROWS = 12


def _pinned_genome() -> np.ndarray:
    return np.random.default_rng(_GENOME_SEED).uniform(size=(_GENOME_ROWS, 2))


def _rollout_snapshot(bundle_id: str, r: RolloutResult) -> dict[str, Any]:
    return {
        "bundle_id": bundle_id,
        "schema": RESULT_SCHEMA,
        "simulation_mode": r.simulation_mode,
        "integral_instability": float(r.integral_instability),
        "collapsed": bool(r.collapsed),
        "attack_cost": float(r.attack_cost),
        "collapse_timestep": r.collapse_timestep,
        "trajectory_steps": len(r.trajectory),
        "rollout_seed": int(r.seed),
    }


def run_aggregate_rollout_v1() -> dict[str, Any]:
    genome = _pinned_genome()
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=28)
    r = rollout_stablecoin(template, genome, seed=_ROLLOUT_SEED, initial_panic=0.05)
    return _rollout_snapshot("aggregate_rollout_v1", r)


def run_network_er_rollout_v1() -> dict[str, Any]:
    genome = _pinned_genome()
    graph, _meta = contagion_graph_from_cli(
        graph_kind="erdos_renyi",
        nodes=16,
        graph_seed=7,
        er_p=0.14,
        ws_k=4,
        ws_p=0.12,
    )
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(16, whale_index=0, whale_frac=0.22),
        contagion_beta=0.36,
        max_steps=26,
    )
    r = rollout_stablecoin_network(template, genome, seed=_ROLLOUT_SEED, base_panic=0.05)
    return _rollout_snapshot("network_er_rollout_v1", r)


def run_network_neighbor_list_rollout_v1() -> dict[str, Any]:
    genome = _pinned_genome()
    nl = [[1], [2], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(3, whale_index=0, whale_frac=0.25),
        contagion_beta=0.35,
        max_steps=24,
    )
    r = rollout_stablecoin_network(template, genome, seed=_ROLLOUT_SEED, base_panic=0.05)
    return _rollout_snapshot("network_neighbor_list_rollout_v1", r)


BUNDLE_RUNNERS: dict[str, Any] = {
    "aggregate_rollout_v1": run_aggregate_rollout_v1,
    "network_er_rollout_v1": run_network_er_rollout_v1,
    "network_neighbor_list_rollout_v1": run_network_neighbor_list_rollout_v1,
}

BUNDLE_IDS: tuple[str, ...] = tuple(sorted(BUNDLE_RUNNERS.keys()))

# Golden metrics captured from Linux reference run; tests use relaxed rtol.
GOLDEN_METRICS: dict[str, dict[str, float | bool]] = {
    "aggregate_rollout_v1": {
        "integral_instability": 2.9225,
        "attack_cost": 6.544042877815768,
        "collapsed": True,
    },
    "network_er_rollout_v1": {
        "integral_instability": 2.9225,
        "attack_cost": 6.544042877815768,
        "collapsed": True,
    },
    "network_neighbor_list_rollout_v1": {
        "integral_instability": 2.9225,
        "attack_cost": 6.544042877815768,
        "collapsed": True,
    },
}


def run_benchmark_suite() -> list[dict[str, Any]]:
    """Execute every registered bundle (deterministic)."""

    return [BUNDLE_RUNNERS[bid]() for bid in BUNDLE_IDS]


def assert_bundle_matches_golden(result: dict[str, Any], *, rtol: float = 1e-5, atol: float = 1e-7) -> None:
    bid = result["bundle_id"]
    gold = GOLDEN_METRICS[bid]
    np.testing.assert_allclose(
        result["integral_instability"],
        float(gold["integral_instability"]),
        rtol=rtol,
        atol=atol,
    )
    np.testing.assert_allclose(
        result["attack_cost"],
        float(gold["attack_cost"]),
        rtol=rtol,
        atol=atol,
    )
    assert result["collapsed"] is gold["collapsed"]


def validate_benchmark_suite(*, rtol: float = 1e-5, atol: float = 1e-7) -> None:
    for bid in BUNDLE_IDS:
        out = BUNDLE_RUNNERS[bid]()
        assert_bundle_matches_golden(out, rtol=rtol, atol=atol)
