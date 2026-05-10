"""Wall-clock timing for representative rollouts (local profiling; not a regression gate).

Use ``--bundle <id>`` or ``--bundle-all`` to time Phase H frozen bundles from ``fragility_engine.benchmarks.suite``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

from fragility_engine.adversary.encoding import random_genome
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.benchmarks.suite import (
    BUNDLE_IDS,
    PINNED_GENOME_SEED,
    PINNED_ROLLOUT_SEED,
    run_bundle_rollout_once,
)
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import (
    resource_cascade_backend_benchmark_meta,
    rollout_resource_cascade,
    rollout_stablecoin,
    rollout_stablecoin_network,
)
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Time aggregate, network, or resource_cascade rollouts (perf_counter). "
            "Optional --bundle / --bundle-all run Phase H golden workloads (ignore --mode sizing)."
        ),
    )
    _bundle_grp = p.add_mutually_exclusive_group()
    _bundle_grp.add_argument(
        "--bundle",
        choices=BUNDLE_IDS,
        default=None,
        help=(
            "Phase H bundle id: same genome seeds + templates as run_benchmark_suite.py "
            f"(genome_seed={PINNED_GENOME_SEED}, rollout_seed={PINNED_ROLLOUT_SEED}). "
            "When set, --mode / --horizon / --seed / topology flags are ignored."
        ),
    )
    _bundle_grp.add_argument(
        "--bundle-all",
        action="store_true",
        help=(
            "Time every Phase H bundle in registry order (same warmup/repeat each); "
            "emits aggregate JSON with per-bundle rows under --json."
        ),
    )
    p.add_argument("--mode", choices=("aggregate", "network", "resource_cascade"), default="network")
    p.add_argument("--warmup", type=int, default=1, help="Ignored iterations before timing.")
    p.add_argument("--repeat", type=int, default=8, help="Timed iterations.")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--horizon", type=int, default=24, help="Attacker schedule length (genome rows).")
    p.add_argument("--max-steps", type=int, default=48)
    p.add_argument("--nodes", type=int, default=96)
    p.add_argument("--graph-kind", choices=("erdos_renyi", "watts_strogatz"), default="erdos_renyi")
    p.add_argument("--graph-seed", type=int, default=7)
    p.add_argument("--er-p", type=float, default=0.1)
    p.add_argument("--ws-k", type=int, default=6)
    p.add_argument("--ws-p", type=float, default=0.12)
    p.add_argument(
        "--neighbor-json",
        type=Path,
        default=None,
        help="[network] list-only topology JSON (skips synthetic graph).",
    )
    p.add_argument("--neighbor-weights-json", type=Path, default=None, help="[network] optional edge weights JSON.")
    p.add_argument(
        "--initial-overload",
        type=float,
        default=0.05,
        help="[resource_cascade] overload at reset [0,1].",
    )
    p.add_argument("--json", action="store_true", help="Emit one JSON object on stdout.")
    args = p.parse_args()

    repeat = max(0, int(args.repeat))
    warmup = max(0, int(args.warmup))

    if args.bundle_all:
        rows: list[dict[str, float | str]] = []
        total_wall = 0.0
        for bid in BUNDLE_IDS:

            def run_once_b(bid_: str = bid) -> None:
                run_bundle_rollout_once(bid_)

            for _ in range(warmup):
                run_once_b()
            t0 = time.perf_counter()
            for _ in range(repeat):
                run_once_b()
            elapsed = time.perf_counter() - t0
            total_wall += elapsed
            mean_ms = (elapsed / repeat * 1000.0) if repeat else 0.0
            rows.append(
                {
                    "bundle_id": bid,
                    "wall_clock_s": elapsed,
                    "mean_ms_per_rollout": mean_ms,
                }
            )
        payload = {
            "workflow": "phase_h_bundle_suite",
            "pinned_genome_seed": PINNED_GENOME_SEED,
            "pinned_rollout_seed": PINNED_ROLLOUT_SEED,
            "repeat": repeat,
            "warmup": warmup,
            "bundle_count": len(rows),
            "bundles": rows,
            "total_wall_clock_s": total_wall,
            "resource_cascade_backend": resource_cascade_backend_benchmark_meta(
                ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=26)
            ),
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Phase H bundle suite  repeat={repeat}  warmup={warmup}  total_wall={total_wall:.4f}s")
            for row in rows:
                print(f"  {row['bundle_id']}: mean={row['mean_ms_per_rollout']:.3f} ms/rollout")
        return

    if args.bundle is not None:

        def run_once() -> None:
            run_bundle_rollout_once(args.bundle)

        for _ in range(warmup):
            run_once()

        t0 = time.perf_counter()
        for _ in range(repeat):
            run_once()
        elapsed = time.perf_counter() - t0

        mean_ms = (elapsed / repeat * 1000.0) if repeat else 0.0
        payload = {
            "workflow": "phase_h_bundle",
            "bundle_id": args.bundle,
            "pinned_genome_seed": PINNED_GENOME_SEED,
            "pinned_rollout_seed": PINNED_ROLLOUT_SEED,
            "repeat": repeat,
            "warmup": warmup,
            "wall_clock_s": elapsed,
            "mean_ms_per_rollout": mean_ms,
        }
        if args.bundle == "resource_cascade_rollout_v1":
            payload["resource_cascade_backend"] = resource_cascade_backend_benchmark_meta(
                ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=26)
            )
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(
                f"bundle={args.bundle}  repeat={repeat}  wall={elapsed:.4f}s  "
                f"mean={mean_ms:.3f} ms/rollout  (Phase H pinned seeds)"
            )
        return

    rng = np.random.default_rng(int(args.seed))
    genome = random_genome(int(args.horizon), rng)
    n_report: int | None = None

    if args.mode == "aggregate":
        template = StablecoinPegWorld(
            population=default_stablecoin_population(),
            max_steps=int(args.max_steps),
        )

        def run_once() -> None:
            rollout_stablecoin(template, genome, seed=int(args.seed))

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
            n_report = len(nl)
            weights = default_whale_weights(n_report, whale_index=0, whale_frac=0.22)
            template = StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                neighbor_lists=nl,
                neighbor_weights=nw,
                node_weights=weights,
                max_steps=int(args.max_steps),
            )
        else:
            try:
                graph, _topo = contagion_graph_from_cli(
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
            n_report = int(args.nodes)
            weights = default_whale_weights(n_report, whale_index=0, whale_frac=0.22)
            template = StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                adjacency=graph,
                node_weights=weights,
                max_steps=int(args.max_steps),
            )

        def run_once() -> None:
            rollout_stablecoin_network(template, genome, seed=int(args.seed))

    else:
        template = ResourceCascadeWorld(
            population=default_stablecoin_population(),
            max_steps=int(args.max_steps),
        )

        def run_once() -> None:
            rollout_resource_cascade(
                template,
                genome,
                seed=int(args.seed),
                initial_overload=float(args.initial_overload),
            )

    for _ in range(warmup):
        run_once()

    t0 = time.perf_counter()
    for _ in range(repeat):
        run_once()
    elapsed = time.perf_counter() - t0

    mean_ms = (elapsed / repeat * 1000.0) if repeat else 0.0
    payload = {
        "workflow": "ad_hoc",
        "mode": args.mode,
        "repeat": repeat,
        "warmup": warmup,
        "wall_clock_s": elapsed,
        "mean_ms_per_rollout": mean_ms,
        "nodes": n_report if args.mode == "network" else None,
        "initial_overload": float(args.initial_overload) if args.mode == "resource_cascade" else None,
        "max_steps": int(args.max_steps),
        "horizon": int(args.horizon),
        "seed": int(args.seed),
    }
    if args.mode == "resource_cascade":
        payload["resource_cascade_backend"] = resource_cascade_backend_benchmark_meta(template)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"mode={args.mode}  repeat={repeat}  wall={elapsed:.4f}s  "
            f"mean={mean_ms:.3f} ms/rollout  (max_steps={args.max_steps} horizon={args.horizon})"
        )


if __name__ == "__main__":
    main()
