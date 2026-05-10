"""Moonshot CLI: ensemble metrics over topology RNG seeds (deterministic per seed)."""

from __future__ import annotations

import argparse
import json

import numpy as np

from fragility_engine.benchmarks.ensemble import (
    robustness_ensemble_1d_param_sweep,
    robustness_ensemble_2d_param_grid,
    robustness_rollouts_over_graph_seeds,
)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Same genome + rollout seed; vary ER/WS graph_seed — summarize dispersion.",
    )
    ap.add_argument("--graph-kind", choices=("erdos_renyi", "watts_strogatz"), default="erdos_renyi")
    ap.add_argument("--nodes", type=int, default=14)
    ap.add_argument(
        "--graph-seeds",
        type=str,
        default="101,102,103",
        help="Comma-separated topology RNG seeds.",
    )
    ap.add_argument(
        "--topology",
        choices=("dense", "neighbor_lists"),
        default="dense",
        help="World topology storage: dense ContagionGraph adjacency vs list-only (**O(edges)** RAM).",
    )
    ap.add_argument("--rollout-seed", type=int, default=5000)
    ap.add_argument("--genome-seed", type=int, default=9001)
    ap.add_argument("--horizon", type=int, default=12)
    ap.add_argument("--er-p", type=float, default=0.12)
    ap.add_argument("--ws-k", type=int, default=4)
    ap.add_argument("--ws-p", type=float, default=0.15)
    ap.add_argument("--beta", type=float, default=0.36)
    ap.add_argument("--whale-frac", type=float, default=0.22)
    ap.add_argument("--base-panic", type=float, default=0.05)
    ap.add_argument("--max-steps", type=int, default=26)
    ap.add_argument(
        "--sweep-param",
        choices=("er_p", "ws_p", "ws_k", "base_panic", "contagion_beta", "whale_frac"),
        default=None,
        help="1D: pair with --sweep-values. 2D: also set --sweep-param-2 and --sweep-values-2.",
    )
    ap.add_argument(
        "--sweep-values",
        type=str,
        default=None,
        help="Comma-separated values for --sweep-param.",
    )
    ap.add_argument(
        "--sweep-param-2",
        choices=("er_p", "ws_p", "ws_k", "base_panic", "contagion_beta", "whale_frac"),
        default=None,
        help="Second axis for 2D grid (must differ from --sweep-param).",
    )
    ap.add_argument(
        "--sweep-values-2",
        type=str,
        default=None,
        help="Comma-separated values for --sweep-param-2.",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    seeds = [int(x.strip()) for x in args.graph_seeds.split(",") if x.strip()]
    if not seeds:
        raise SystemExit("Provide at least one --graph-seeds value.")

    sweep_1 = args.sweep_param is not None or args.sweep_values is not None
    sweep_2_axis = args.sweep_param_2 is not None or args.sweep_values_2 is not None
    if sweep_1 != bool(args.sweep_param and args.sweep_values):
        raise SystemExit("Use --sweep-param and --sweep-values together for 1D/2D, or omit all sweep flags.")
    if sweep_2_axis != bool(args.sweep_param_2 and args.sweep_values_2):
        raise SystemExit("Use --sweep-param-2 and --sweep-values-2 together, or omit both.")
    if sweep_2_axis and not sweep_1:
        raise SystemExit("2D grid requires --sweep-param, --sweep-values, --sweep-param-2, and --sweep-values-2.")
    if args.sweep_param and args.sweep_param_2 and args.sweep_param == args.sweep_param_2:
        raise SystemExit("--sweep-param and --sweep-param-2 must differ.")

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))

    topo = str(args.topology)
    common = dict(
        graph_kind=str(args.graph_kind),
        nodes=int(args.nodes),
        graph_seeds=seeds,
        rollout_seed=int(args.rollout_seed),
        er_p=float(args.er_p),
        ws_k=int(args.ws_k),
        ws_p=float(args.ws_p),
        base_panic=float(args.base_panic),
        contagion_beta=float(args.beta),
        whale_frac=float(args.whale_frac),
        max_steps=int(args.max_steps),
        topology_representation=topo,
    )

    if args.sweep_param is not None and args.sweep_param_2 is not None:
        vx = [float(x.strip()) for x in str(args.sweep_values).split(",") if x.strip()]
        vy = [float(x.strip()) for x in str(args.sweep_values_2).split(",") if x.strip()]
        if not vx or not vy:
            raise SystemExit("Both sweep value lists must have at least one number.")
        payload = robustness_ensemble_2d_param_grid(
            genome,
            sweep_param_x=str(args.sweep_param),
            sweep_values_x=vx,
            sweep_param_y=str(args.sweep_param_2),
            sweep_values_y=vy,
            **common,
        )
    elif args.sweep_param is not None:
        sweep_vals = [float(x.strip()) for x in str(args.sweep_values).split(",") if x.strip()]
        if not sweep_vals:
            raise SystemExit("--sweep-values must list at least one number.")
        payload = robustness_ensemble_1d_param_sweep(
            genome,
            sweep_param=str(args.sweep_param),
            sweep_values=sweep_vals,
            **common,
        )
    else:
        payload = robustness_rollouts_over_graph_seeds(genome, **common)

    payload["genome_seed"] = int(args.genome_seed)
    payload["horizon"] = int(args.horizon)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        sch = payload.get("schema", "")
        if sch == "fragility-robustness-sensitivity-2d-v1":
            for pt in payload["points"]:
                s = pt["ensemble"]["summary"]
                print(
                    f"x={pt['sweep_x']:.6g} y={pt['sweep_y']:.6g} "
                    f"collapse_rate={s['collapse_rate']:.3f} "
                    f"integral_p50={s['integral_instability_p50']:.6f}"
                )
            sp = payload["summary"]
            print(
                f"--- grid {sp['grid_cells']} cells collapse_rate in "
                f"[{sp['collapse_rate_min']:.3f}, {sp['collapse_rate_max']:.3f}] "
                f"spread={sp['collapse_rate_spread']:.3f}"
            )
        elif sch == "fragility-robustness-sensitivity-1d-v1":
            for pt in payload["points"]:
                s = pt["ensemble"]["summary"]
                print(
                    f"{args.sweep_param}={pt['sweep_value']:.6g} "
                    f"collapse_rate={s['collapse_rate']:.3f} "
                    f"integral_p50={s['integral_instability_p50']:.6f}"
                )
            sp = payload["summary"]
            print(
                f"--- collapse_rate in [{sp['collapse_rate_min']:.3f}, {sp['collapse_rate_max']:.3f}] "
                f"spread={sp['collapse_rate_spread']:.3f}"
            )
        else:
            s = payload["summary"]
            print(
                f"runs={s['count']} collapse_rate={s['collapse_rate']:.3f} "
                f"integral p50={s['integral_instability_p50']:.6f} "
                f"[{s['integral_instability_min']:.6f}, {s['integral_instability_max']:.6f}]"
            )


if __name__ == "__main__":
    main()
