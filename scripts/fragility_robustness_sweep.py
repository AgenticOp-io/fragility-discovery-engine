"""Moonshot CLI: ensemble metrics over topology RNG seeds (deterministic per seed)."""

from __future__ import annotations

import argparse
import json

import numpy as np

from fragility_engine.benchmarks.ensemble import robustness_rollouts_over_graph_seeds


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
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    seeds = [int(x.strip()) for x in args.graph_seeds.split(",") if x.strip()]
    if not seeds:
        raise SystemExit("Provide at least one --graph-seeds value.")

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))

    payload = robustness_rollouts_over_graph_seeds(
        genome,
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
    )
    payload["genome_seed"] = int(args.genome_seed)
    payload["horizon"] = int(args.horizon)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        s = payload["summary"]
        print(
            f"runs={s['count']} collapse_rate={s['collapse_rate']:.3f} "
            f"integral p50={s['integral_instability_p50']:.6f} "
            f"[{s['integral_instability_min']:.6f}, {s['integral_instability_max']:.6f}]"
        )


if __name__ == "__main__":
    main()
