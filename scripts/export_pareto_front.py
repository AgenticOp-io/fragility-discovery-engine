"""Run a short GA with Pareto archiving (severity vs attack cost) and dump JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import (
    thread_safe_network_clone,
    thread_safe_peg_clone,
    thread_safe_resource_cascade_clone,
)
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import (
    REPLAY_SCHEMA_VERSION,
    rollout_resource_cascade,
    rollout_stablecoin,
    rollout_stablecoin_network,
    rollout_to_replay_dict,
)
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_network import (
    StablecoinNetworkWorld,
    default_whale_weights,
    neighbor_lists_topology_meta,
)
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    ap = argparse.ArgumentParser(description="Pareto archive dump + optional replay export.")
    ap.add_argument("--out", type=Path, default=Path("pareto_front.json"))
    ap.add_argument("--seed", type=int, default=606, help="GA search seed.")
    ap.add_argument("--horizon", type=int, default=18, help="Attacker schedule rows (genome).")
    ap.add_argument("--generations", type=int, default=10)
    ap.add_argument("--population-size", type=int, default=22)
    ap.add_argument("--max-steps", type=int, default=36, help="World simulation horizon cap.")
    ap.add_argument("--export-replay", type=Path, default=None, help="Export one rollout as replay JSON.")
    ap.add_argument(
        "--replay-pareto-index",
        type=int,
        default=None,
        help="Export pareto_archive[index] rollout (re-evaluated); default is best-fitness rollout.",
    )
    ap.add_argument("--mode", choices=("aggregate", "network", "resource_cascade"), default="aggregate")
    ap.add_argument("--initial-panic", type=float, default=0.05, help="[aggregate] reset panic.")
    ap.add_argument("--base-panic", type=float, default=0.05, help="[network] uniform panic at reset.")
    ap.add_argument("--initial-overload", type=float, default=0.05, help="[resource_cascade] reset overload [0,1].")
    ap.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="Forward rollouts after collapse when applicable.",
    )
    ap.add_argument("--nodes", type=int, default=32, help="[network] graph order (synthetic).")
    ap.add_argument(
        "--graph-kind",
        choices=("erdos_renyi", "watts_strogatz"),
        default="erdos_renyi",
    )
    ap.add_argument("--er-p", type=float, default=0.14)
    ap.add_argument("--ws-k", type=int, default=6)
    ap.add_argument("--ws-p", type=float, default=0.12)
    ap.add_argument("--graph-seed", type=int, default=2026)
    ap.add_argument("--beta", type=float, default=0.38)
    ap.add_argument("--whale-frac", type=float, default=0.22)
    ap.add_argument("--whale-index", type=int, default=0)
    ap.add_argument("--neighbor-json", type=Path, default=None)
    ap.add_argument("--neighbor-weights-json", type=Path, default=None)
    ap.add_argument(
        "--eval-workers",
        type=int,
        default=1,
        help="Thread pool size for GA fitness evaluation (clone per eval when >1).",
    )
    args = ap.parse_args()

    ew = max(1, int(args.eval_workers))
    ms = max(int(args.max_steps), int(args.horizon))
    topo_meta: dict | None = None

    if args.mode == "aggregate":
        template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=ms)

        def evaluator(genome: np.ndarray, seed: int):
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

            try:
                nl, nw = load_neighbor_topology(
                    Path(args.neighbor_json),
                    Path(args.neighbor_weights_json) if args.neighbor_weights_json else None,
                )
            except (ValueError, OSError, json.JSONDecodeError) as e:
                print(str(e), file=sys.stderr)
                raise SystemExit(2) from e
            n = len(nl)
            weights = default_whale_weights(
                n,
                whale_index=int(args.whale_index),
                whale_frac=float(args.whale_frac),
            )
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
            weights = default_whale_weights(
                n,
                whale_index=int(args.whale_index),
                whale_frac=float(args.whale_frac),
            )
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

        def evaluator(genome: np.ndarray, seed: int):
            world = thread_safe_network_clone(template) if ew > 1 else template
            return rollout_stablecoin_network(
                world,
                genome,
                seed=seed,
                base_panic=float(args.base_panic),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    else:
        template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=ms)

        def evaluator(genome: np.ndarray, seed: int):
            world = thread_safe_resource_cascade_clone(template) if ew > 1 else template
            return rollout_resource_cascade(
                world,
                genome,
                seed=seed,
                initial_overload=float(args.initial_overload),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    search = genetic_search(
        evaluator,
        horizon=int(args.horizon),
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
        collect_pareto=True,
        eval_workers=ew,
    )

    payload = {
        "schema": "pareto-front-v1",
        "best_fitness": search.best_fitness,
        "archive": [
            {
                "severity": p.severity,
                "attack_cost": p.attack_cost,
                "collapsed": p.collapsed,
                "integral_instability": p.integral_instability,
                "genome": p.genome.tolist(),
            }
            for p in search.pareto_archive
        ],
    }
    if args.mode == "network" and topo_meta is not None:
        payload["topology"] = topo_meta
    if args.mode == "resource_cascade":
        payload["domain"] = "resource_cascade"
        payload["initial_overload"] = float(args.initial_overload)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay is not None:
        if args.replay_pareto_index is not None:
            idx = int(args.replay_pareto_index)
            arch = search.pareto_archive
            if idx < 0 or idx >= len(arch):
                raise SystemExit(f"--replay-pareto-index in [0, {len(arch) - 1}] (got {idx}).")
            rr = evaluator(arch[idx].genome, args.seed + 40_000 + idx)
            meta_extra = {"pareto_index": idx, "severity": arch[idx].severity, "attack_cost": arch[idx].attack_cost}
        else:
            rr = search.best_rollout
            meta_extra = {"source": "best_fitness"}
        replay = rollout_to_replay_dict(rr)
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_pareto_front",
            "pareto_front_seed": args.seed,
            "mode": args.mode,
            **meta_extra,
        }
        if topo_meta is not None:
            replay["meta"]["topology"] = topo_meta
        if args.mode == "resource_cascade":
            replay["meta"]["domain"] = "resource_cascade"
            replay["meta"]["initial_overload"] = float(args.initial_overload)
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
