from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    compare_rollouts,
    counterfactual_bundle_to_jsonable,
    counterfactual_remove_steps,
    genome_zero_timesteps,
    rollout_snapshot,
)
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_genome_zero_timesteps_idempotent_subset():
    g = np.random.default_rng(2).uniform(size=(10, 2))
    z = genome_zero_timesteps(g, [1, 3, 1])
    assert np.allclose(z[1], [0.0, 0.0])
    assert np.allclose(z[3], [0.0, 0.0])
    zz = genome_zero_timesteps(z, [])
    assert np.allclose(z, zz)


def test_rollout_snapshot_has_integral_and_horizon():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=12)
    genome = np.zeros((12, 2))

    def ev(g: np.ndarray, s: int):
        return rollout_stablecoin(template, g, seed=s)

    r = ev(genome, 100)
    snap = rollout_snapshot(r)
    assert snap["integral_instability"] == r.integral_instability
    assert snap["horizon_steps"] == len(r.trajectory)


def test_compare_rollouts_nested_snapshots():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=8)
    genome = np.zeros((8, 2))

    def ev(g: np.ndarray, s: int):
        return rollout_stablecoin(template, g, seed=s)

    a = ev(genome, 7)
    b = ev(genome, 99)
    out = compare_rollouts(a, b, label_base="first", label_variant="second")
    assert "integral_instability" in out["first"]
    assert out["second"]["seed"] == 99


def test_counterfactual_removal_reduces_attack_cost_when_shocks_cleared():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=20)

    def ev(g: np.ndarray, s: int):
        return rollout_stablecoin(template, g, seed=s)

    genome = np.random.default_rng(404).uniform(size=(20, 2))
    report = counterfactual_remove_steps(genome, ev, remove_timesteps=list(range(20)), base_seed=9090)
    assert report["counterfactual"]["attack_cost"] == 0.0
    assert report["baseline"]["attack_cost"] >= 0.0
    assert report["delta_attack_cost"] >= 0.0
    assert report["removed_timesteps"] == list(range(20))


def test_counterfactual_bundle_jsonable_roundtrip_keys():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=16)

    def ev(g: np.ndarray, s: int):
        return rollout_stablecoin(template, g, seed=s)

    genome = np.ones((16, 2)) * 0.4
    report = counterfactual_remove_steps(genome, ev, remove_timesteps=[0, 2], base_seed=51)
    blob = counterfactual_bundle_to_jsonable(report)
    assert set(blob.keys()) >= {"baseline", "counterfactual", "removed_timesteps", "delta_attack_cost"}
