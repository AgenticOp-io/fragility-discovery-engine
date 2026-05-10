"""Phase K optional threaded batching — ordering + determinism vs sequential."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.parallel_rollouts import process_pool_map_ordered, thread_pool_map_ordered
from fragility_engine.runner import rollout_resource_cascade
from fragility_engine.world.resource_cascade import ResourceCascadeWorld


def test_thread_pool_map_ordered_empty():
    assert thread_pool_map_ordered(lambda x: x, [], max_workers=4) == []


def test_thread_pool_map_ordered_matches_sequential_resource_cascade():
    genome = np.random.default_rng(777).uniform(size=(8, 2))
    seeds = [91001, 91002, 91003, 91004]

    def one(seed: int) -> float:
        w = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=18)
        return float(rollout_resource_cascade(w, genome, seed=seed, initial_overload=0.055).integral_instability)

    seq = [one(s) for s in seeds]
    par = thread_pool_map_ordered(one, seeds, max_workers=4)
    assert par == seq


def _proc_square(x: int) -> int:
    return x * x


def test_process_pool_map_ordered_matches_sequential():
    items = list(range(8))
    seq = [_proc_square(x) for x in items]
    par = process_pool_map_ordered(_proc_square, items, max_workers=3)
    assert par == seq


def test_thread_pool_map_ordered_single_worker_is_sequential():
    calls: list[int] = []

    def rec(x: int) -> int:
        calls.append(x)
        return x * 2

    out = thread_pool_map_ordered(rec, [3, 1, 2], max_workers=1)
    assert out == [6, 2, 4]
    assert calls == [3, 1, 2]
