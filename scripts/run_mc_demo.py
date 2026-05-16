"""Monte Carlo random shock schedules — aggregate, network, resource_cascade, or service_backlog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.adversary.search import monte_carlo_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import (
    thread_safe_liquidity_ladder_clone,
    thread_safe_network_clone,
    thread_safe_peg_clone,
    thread_safe_resource_cascade_clone,
    thread_safe_service_backlog_clone,
)
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import (
    REPLAY_SCHEMA_VERSION,
    rollout_liquidity_ladder,
    rollout_resource_cascade,
    rollout_service_backlog,
    rollout_stablecoin,
    rollout_stablecoin_network,
    rollout_to_replay_dict,
)
from fragility_engine.types import RolloutResult
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.service_backlog import ServiceBacklogWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(
        description="Monte Carlo search over random genomes (aggregate, network, resource_cascade, or service_backlog)."
    )
    p.add_argument(
        "--mode",
        choices=("aggregate", "network", "resource_cascade", "service_backlog", "liquidity_ladder"),
        default="aggregate",
    )
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--horizon", type=int, default=20)
    p.add_argument("--seed", type=int, default=303)
    p.add_argument("--export-replay", type=Path, default=None, help="Write best-sample rollout JSON.")
    p.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="Forward past collapse for recovery fields when applicable.",
    )
    p.add_argument(
        "--eval-workers",
        type=int,
        default=1,
        help="Pool size for MC trial evaluation (thread-safe world clones when >1).",
    )
    p.add_argument(
        "--eval-pool",
        choices=("threads", "processes"),
        default="threads",
        help="threads (default) or processes (requires picklable rollout_fn; use bundle benchmarks for process MC).",
    )
    p.add_argument("--max-steps", type=int, default=40, help="World horizon cap (all modes).")
    p.add_argument("--initial-panic", type=float, default=0.05, help="[aggregate] reset panic.")
    p.add_argument("--base-panic", type=float, default=0.05, help="[network] uniform panic at reset.")
    p.add_argument("--initial-overload", type=float, default=0.05, help="[resource_cascade] reset overload [0,1].")
    p.add_argument("--initial-backlog", type=float, default=0.05, help="[service_backlog] reset backlog.")
    p.add_argument("--initial-margin", type=float, default=0.06, help="[liquidity_ladder] reset margin utilization.")
    p.add_argument("--nodes", type=int, default=32, help="[network] graph order (synthetic).")
    p.add_argument(
        "--graph-kind",
        choices=("erdos_renyi", "watts_strogatz"),
        default="erdos_renyi",
    )
    p.add_argument("--er-p", type=float, default=0.12)
    p.add_argument("--ws-k", type=int, default=6)
    p.add_argument("--ws-p", type=float, default=0.15)
    p.add_argument("--graph-seed", type=int, default=2026)
    p.add_argument("--beta", type=float, default=0.38)
    p.add_argument("--whale-frac", type=float, default=0.24)
    p.add_argument("--neighbor-json", type=Path, default=None, help="[network] list-only topology JSON.")
    p.add_argument("--neighbor-weights-json", type=Path, default=None, help="[network] optional edge weights JSON.")
    args = p.parse_args()
    ew = max(1, int(args.eval_workers))
    ms = max(int(args.max_steps), int(args.horizon))
    topo_meta: dict | None = None

    if args.mode == "aggregate":
        template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=ms)

        def evaluator(genome: np.ndarray, seed: int) -> RolloutResult:
            world = thread_safe_peg_clone(template) if ew > 1 else template
            return rollout_stablecoin(
                world,
                genome,
                seed=seed,
                initial_panic=float(args.initial_panic),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    elif args.mode == "network":
        if args.neighbor_json is not None:
            from fragility_engine.network.neighbor_io import load_neighbor_topology
            from fragility_engine.world.stablecoin_network import neighbor_lists_topology_meta

            try:
                nl, nw = load_neighbor_topology(
                    Path(args.neighbor_json),
                    Path(args.neighbor_weights_json) if args.neighbor_weights_json else None,
                )
            except (ValueError, OSError, json.JSONDecodeError) as e:
                print(str(e), file=sys.stderr)
                raise SystemExit(2) from e
            n = len(nl)
            weights = default_whale_weights(n, whale_index=0, whale_frac=float(args.whale_frac))
            template = StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                neighbor_lists=nl,
                neighbor_weights=nw,
                node_weights=weights,
                contagion_beta=float(args.beta),
                max_steps=ms,
            )
            topo_meta = neighbor_lists_topology_meta(nl, weighted=nw is not None)
        else:
            try:
                graph, gen_meta = contagion_graph_from_cli(
                    graph_kind=str(args.graph_kind),
                    nodes=int(args.nodes),
                    graph_seed=int(args.graph_seed),
                    er_p=float(args.er_p),
                    ws_k=int(args.ws_k),
                    ws_p=float(args.ws_p),
                )
            except ValueError as e:
                print(str(e), file=sys.stderr)
                raise SystemExit(2) from e
            n = int(args.nodes)
            weights = default_whale_weights(n, whale_index=0, whale_frac=float(args.whale_frac))
            template = StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                adjacency=graph,
                node_weights=weights,
                contagion_beta=float(args.beta),
                max_steps=ms,
            )
            topo_meta = {
                **gen_meta,
                "undirected_edges": graph.undirected_edge_count(),
                "storage": "dense_adjacency",
            }

        def evaluator(genome: np.ndarray, seed: int) -> RolloutResult:
            world = thread_safe_network_clone(template) if ew > 1 else template
            return rollout_stablecoin_network(
                world,
                genome,
                seed=seed,
                base_panic=float(args.base_panic),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    elif args.mode == "resource_cascade":
        template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=ms)

        def evaluator(genome: np.ndarray, seed: int) -> RolloutResult:
            world = thread_safe_resource_cascade_clone(template) if ew > 1 else template
            return rollout_resource_cascade(
                world,
                genome,
                seed=seed,
                initial_overload=float(args.initial_overload),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    elif args.mode == "service_backlog":
        template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=ms)

        def evaluator(genome: np.ndarray, seed: int) -> RolloutResult:
            world = thread_safe_service_backlog_clone(template) if ew > 1 else template
            return rollout_service_backlog(
                world,
                genome,
                seed=seed,
                initial_backlog=float(args.initial_backlog),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    else:
        template = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=ms)

        def evaluator(genome: np.ndarray, seed: int) -> RolloutResult:
            world = thread_safe_liquidity_ladder_clone(template) if ew > 1 else template
            return rollout_liquidity_ladder(
                world,
                genome,
                seed=seed,
                initial_margin=float(args.initial_margin),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    search = monte_carlo_search(
        evaluator,
        horizon=int(args.horizon),
        samples=int(args.samples),
        seed=int(args.seed),
        eval_workers=ew,
        eval_pool=str(args.eval_pool),
    )

    print(
        json.dumps(
            {
                "best_fitness": search.best_fitness,
                "collapsed": search.best_rollout.collapsed,
                "collapse_timestep": search.best_rollout.collapse_timestep,
                "attack_cost": search.best_rollout.attack_cost,
                "mode": str(args.mode),
            },
            indent=2,
        )
    )

    if args.export_replay is not None:
        replay = rollout_to_replay_dict(search.best_rollout)
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "run_mc_demo",
            "samples": int(args.samples),
            "horizon": int(args.horizon),
            "mc_seed": int(args.seed),
            "eval_workers": ew,
            "eval_pool": str(args.eval_pool),
            "simulation_mode": str(args.mode),
        }
        if topo_meta is not None:
            replay["meta"]["topology"] = topo_meta
        if args.mode == "resource_cascade":
            replay["meta"]["initial_overload"] = float(args.initial_overload)
        if args.mode == "service_backlog":
            replay["meta"]["initial_backlog"] = float(args.initial_backlog)
        if args.mode == "liquidity_ladder":
            replay["meta"]["initial_margin"] = float(args.initial_margin)
        if args.mode == "aggregate":
            replay["meta"]["initial_panic"] = float(args.initial_panic)
        if args.mode == "network":
            replay["meta"]["base_panic"] = float(args.base_panic)
        if args.continue_after_collapse:
            replay["meta"]["continue_after_collapse"] = True
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
