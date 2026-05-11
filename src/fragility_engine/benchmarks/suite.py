"""Frozen deterministic bundles for reproducibility regression (Phase H)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import (
    thread_safe_network_clone,
    thread_safe_peg_clone,
    thread_safe_resource_cascade_clone,
    thread_safe_service_backlog_clone,
)
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import (
    rollout_resource_cascade,
    rollout_service_backlog,
    rollout_stablecoin,
    rollout_stablecoin_network,
)
from fragility_engine.types import RolloutResult
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.service_backlog import ServiceBacklogWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld

RESULT_SCHEMA = "benchmark-bundle-result-v1"

# Pin genome + rollout seed so CI matches local; tolerances in tests absorb tiny FP drift.
PINNED_GENOME_SEED = 9001
PINNED_ROLLOUT_SEED = 4242
_GENOME_ROWS = 12
# Schedule rows for pinned genome / Phase H bundles (encoding width).
PINNED_SCHEDULE_HORIZON = _GENOME_ROWS


def _pinned_genome() -> np.ndarray:
    return np.random.default_rng(PINNED_GENOME_SEED).uniform(size=(_GENOME_ROWS, 2))


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


def rollout_bundle_with_genome(
    bundle_id: str,
    genome: np.ndarray,
    seed: int,
    *,
    isolate: bool = False,
) -> RolloutResult:
    """Run one rollout for a Phase H bundle with caller-supplied genome and seed.

    ``isolate=True`` uses a fresh :class:`~fragility_engine.agents.stablecoin_agents.AgentPopulation`
    per call (safe for process- or thread-parallel search). ``isolate=False`` matches
    :func:`run_bundle_rollout_once` single-template semantics (pinned golden bundles).
    """

    if bundle_id == "aggregate_rollout_v1":
        base = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=28)
        world = thread_safe_peg_clone(base) if isolate else base
        return rollout_stablecoin(world, genome, seed=seed, initial_panic=0.05)
    if bundle_id == "network_er_rollout_v1":
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
        world = thread_safe_network_clone(template) if isolate else template
        return rollout_stablecoin_network(world, genome, seed=seed, base_panic=0.05)
    if bundle_id == "network_neighbor_list_rollout_v1":
        nl = [[1], [2], [0]]
        template = StablecoinNetworkWorld(
            population=default_stablecoin_population(),
            neighbor_lists=nl,
            node_weights=default_whale_weights(3, whale_index=0, whale_frac=0.25),
            contagion_beta=0.35,
            max_steps=24,
        )
        world = thread_safe_network_clone(template) if isolate else template
        return rollout_stablecoin_network(world, genome, seed=seed, base_panic=0.05)
    if bundle_id == "resource_cascade_rollout_v1":
        template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=26)
        world = thread_safe_resource_cascade_clone(template) if isolate else template
        return rollout_resource_cascade(world, genome, seed=seed, initial_overload=0.05)
    if bundle_id == "service_backlog_rollout_v1":
        template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=26)
        world = thread_safe_service_backlog_clone(template) if isolate else template
        return rollout_service_backlog(world, genome, seed=seed, initial_backlog=0.05)
    raise ValueError(f"unknown bundle_id {bundle_id!r}")


def run_bundle_rollout_once(bundle_id: str) -> RolloutResult:
    """Execute exactly one rollout for a Phase H bundle id (pinned genome + seeds)."""

    return rollout_bundle_with_genome(bundle_id, _pinned_genome(), PINNED_ROLLOUT_SEED, isolate=False)


def bundle_search_evaluator(
    bundle_id: str,
    *,
    eval_workers: int = 1,
) -> Callable[[np.ndarray, int], RolloutResult]:
    """
    Rollout closure for timing ``monte_carlo_search`` / ``genetic_search`` on a Phase H bundle world.

    When ``eval_workers > 1``, builds a fresh population clone per call (same physics/topology as
    :func:`run_bundle_rollout_once`).
    """

    ew = max(1, int(eval_workers))
    isolate = ew > 1

    def evaluator(g: np.ndarray, seed: int) -> RolloutResult:
        return rollout_bundle_with_genome(bundle_id, g, seed, isolate=isolate)

    return evaluator


def run_aggregate_rollout_v1() -> dict[str, Any]:
    r = run_bundle_rollout_once("aggregate_rollout_v1")
    return _rollout_snapshot("aggregate_rollout_v1", r)


def run_network_er_rollout_v1() -> dict[str, Any]:
    r = run_bundle_rollout_once("network_er_rollout_v1")
    return _rollout_snapshot("network_er_rollout_v1", r)


def run_network_neighbor_list_rollout_v1() -> dict[str, Any]:
    r = run_bundle_rollout_once("network_neighbor_list_rollout_v1")
    return _rollout_snapshot("network_neighbor_list_rollout_v1", r)


def run_resource_cascade_rollout_v1() -> dict[str, Any]:
    r = run_bundle_rollout_once("resource_cascade_rollout_v1")
    return _rollout_snapshot("resource_cascade_rollout_v1", r)


def run_service_backlog_rollout_v1() -> dict[str, Any]:
    r = run_bundle_rollout_once("service_backlog_rollout_v1")
    return _rollout_snapshot("service_backlog_rollout_v1", r)


BUNDLE_RUNNERS: dict[str, Any] = {
    "aggregate_rollout_v1": run_aggregate_rollout_v1,
    "network_er_rollout_v1": run_network_er_rollout_v1,
    "network_neighbor_list_rollout_v1": run_network_neighbor_list_rollout_v1,
    "resource_cascade_rollout_v1": run_resource_cascade_rollout_v1,
    "service_backlog_rollout_v1": run_service_backlog_rollout_v1,
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
    "resource_cascade_rollout_v1": {
        "integral_instability": 6.129501695143888,
        "attack_cost": 6.544042877815768,
        "collapsed": True,
    },
    "service_backlog_rollout_v1": {
        "integral_instability": 0.33630575509480504,
        "attack_cost": 6.544042877815768,
        "collapsed": False,
    },
}

# Slightly looser tolerances for bundles whose FP reductions differ across platforms (Linux CI).
BUNDLE_GOLDEN_RTOL: dict[str, float] = {
    "resource_cascade_rollout_v1": 2e-4,
}
BUNDLE_GOLDEN_ATOL: dict[str, float] = {
    "resource_cascade_rollout_v1": 1e-6,
}


def run_benchmark_suite() -> list[dict[str, Any]]:
    """Execute every registered bundle (deterministic)."""

    return [BUNDLE_RUNNERS[bid]() for bid in BUNDLE_IDS]


def assert_bundle_matches_golden(result: dict[str, Any], *, rtol: float = 1e-5, atol: float = 1e-7) -> None:
    bid = result["bundle_id"]
    gold = GOLDEN_METRICS[bid]
    rto = BUNDLE_GOLDEN_RTOL.get(bid, rtol)
    ato = BUNDLE_GOLDEN_ATOL.get(bid, atol)
    np.testing.assert_allclose(
        result["integral_instability"],
        float(gold["integral_instability"]),
        rtol=rto,
        atol=ato,
    )
    np.testing.assert_allclose(
        result["attack_cost"],
        float(gold["attack_cost"]),
        rtol=rto,
        atol=ato,
    )
    assert result["collapsed"] is gold["collapsed"]


def run_phase_h_search_microbench(
    *,
    bench_search: str,
    bundle_ids: tuple[str, ...] | None = None,
    eval_workers: int = 1,
    eval_pool: str = "threads",
    search_seed: int | None = None,
    generations: int = 2,
    population_size: int = 8,
    samples: int = 16,
) -> dict[str, Any]:
    """
    One-shot Phase H search microbench (same semantics as ``benchmark_rollout.py --bench-search``).

    Intended for ``run_benchmark_suite.py --bench-search`` and scripting; not a CI golden gate.
    """

    import time
    from functools import partial

    from fragility_engine.adversary.search import genetic_search, monte_carlo_search

    bs = bench_search.strip().lower()
    if bs not in ("mc", "ga"):
        raise ValueError("bench_search must be 'mc' or 'ga'")
    pool = eval_pool.strip().lower()
    if pool not in ("threads", "processes"):
        raise ValueError("eval_pool must be 'threads' or 'processes'")
    ew = max(1, int(eval_workers))
    bids = tuple(bundle_ids) if bundle_ids is not None else BUNDLE_IDS
    seed_ = PINNED_GENOME_SEED if search_seed is None else int(search_seed)
    sg = max(1, int(generations))
    sp = max(2, int(population_size))
    ss = max(0, int(samples))
    rows: list[dict[str, float | str]] = []
    total_wall = 0.0
    for bid in bids:
        if pool == "processes" and ew > 1:
            rollout = partial(rollout_bundle_with_genome, bid, isolate=True)
        else:
            rollout = bundle_search_evaluator(bid, eval_workers=ew)
        t0 = time.perf_counter()
        if bs == "ga":
            genetic_search(
                rollout,
                horizon=PINNED_SCHEDULE_HORIZON,
                generations=sg,
                population_size=sp,
                seed=seed_,
                eval_workers=ew,
                eval_pool=pool,  # type: ignore[arg-type]
            )
        else:
            monte_carlo_search(
                rollout,
                horizon=PINNED_SCHEDULE_HORIZON,
                samples=ss,
                seed=seed_,
                eval_workers=ew,
                eval_pool=pool,  # type: ignore[arg-type]
            )
        elapsed = time.perf_counter() - t0
        total_wall += elapsed
        rows.append({"bundle_id": bid, "wall_clock_s": elapsed, "mean_ms_per_search": elapsed * 1000.0})
    payload: dict[str, Any] = {
        "workflow": "phase_h_bundle_search_microbench",
        "bench_search": bs,
        "eval_workers": ew,
        "eval_pool": pool,
        "search_seed": seed_,
        "pinned_schedule_horizon": PINNED_SCHEDULE_HORIZON,
        "bundles": rows,
        "total_wall_clock_s": total_wall,
    }
    if bs == "ga":
        payload["search_generations"] = sg
        payload["search_population"] = sp
    else:
        payload["search_samples"] = ss
    return payload


def validate_benchmark_suite(*, rtol: float = 1e-5, atol: float = 1e-7) -> None:
    for bid in BUNDLE_IDS:
        out = BUNDLE_RUNNERS[bid]()
        assert_bundle_matches_golden(out, rtol=rtol, atol=atol)
