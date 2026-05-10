"""Moonshot CLI: ensemble metrics over topology RNG seeds (deterministic per seed)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.benchmarks.ensemble import (
    robustness_ensemble_1d_param_sweep,
    robustness_ensemble_2d_param_grid,
    robustness_ga_budget_2d_grid,
    robustness_ga_generations_1d_sweep,
    robustness_ga_population_1d_sweep,
    robustness_rollouts_neighbor_json_bundle,
    robustness_rollouts_over_graph_seeds,
)

_SYNTHETIC_ONLY_KEYS = frozenset({"neighbor_json_paths", "neighbor_weights_json_paths"})


def _parse_neighbor_bundle_paths(s: str) -> list[Path]:
    paths = [Path(x.strip()) for x in s.split(",") if x.strip()]
    if not paths:
        raise SystemExit("--neighbor-json-list must list at least one existing-path candidate.")
    return paths


def _parse_neighbor_weights_bundle(s: str | None, n: int) -> list[Path | None] | None:
    if s is None:
        return None
    parts = [x.strip() for x in s.split(",")]
    if len(parts) != n:
        raise SystemExit(
            f"--neighbor-weights-json-list must have {n} comma-separated entries "
            "(use none or - for no weights file)."
        )
    out: list[Path | None] = []
    for p in parts:
        if p.lower() in ("", "none", "-"):
            out.append(None)
        else:
            out.append(Path(p))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Same genome + rollout seed; vary ER/WS graph_seed; summarize dispersion.",
    )
    ap.add_argument("--graph-kind", choices=("erdos_renyi", "watts_strogatz"), default="erdos_renyi")
    ap.add_argument("--nodes", type=int, default=14)
    ap.add_argument(
        "--graph-seeds",
        type=str,
        default="101,102,103",
        help="Comma-separated topology RNG seeds (ignored when --neighbor-json-list is set).",
    )
    ap.add_argument(
        "--neighbor-json-list",
        type=str,
        default=None,
        help="Comma-separated neighbor-list JSON paths; each file is one ensemble member (list topology).",
    )
    ap.add_argument(
        "--neighbor-weights-json-list",
        type=str,
        default=None,
        help="Optional weights JSON paths, same length as --neighbor-json-list (none/-/empty slot = unweighted).",
    )
    ap.add_argument(
        "--topology",
        choices=("dense", "neighbor_lists"),
        default="dense",
        help="Synthetic mode only: dense ContagionGraph adjacency vs list-only (**O(edges)** RAM).",
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
    ap.add_argument(
        "--ga-budget-sweep",
        action="store_true",
        help="1D: sweep GA generations with fixed --ga-population-size (train / ensemble-eval).",
    )
    ap.add_argument(
        "--ga-budget-2d",
        action="store_true",
        help="2D grid: --ga-generations-values x --ga-population-values (mutually exclusive with other GA modes).",
    )
    ap.add_argument(
        "--ga-population-sweep",
        action="store_true",
        help="1D: sweep GA population sizes with fixed --ga-fixed-generations (train / ensemble-eval).",
    )
    ap.add_argument(
        "--ga-fixed-generations",
        type=int,
        default=4,
        help="With --ga-population-sweep: inner GA generation count (fixed across population sweep).",
    )
    ap.add_argument(
        "--ga-generations-values",
        type=str,
        default=None,
        help="Comma-separated positive ints; use with --ga-budget-sweep or --ga-budget-2d.",
    )
    ap.add_argument(
        "--ga-population-values",
        type=str,
        default=None,
        help="Comma-separated ints >=2; requires --ga-budget-2d or --ga-population-sweep.",
    )
    ap.add_argument("--ga-population-size", type=int, default=16)
    ap.add_argument("--ga-seed", type=int, default=7001)
    ap.add_argument(
        "--train-graph-seed",
        type=int,
        default=None,
        help="Synthetic mode only: ER/WS seed for inner GA training (default: first --graph-seeds).",
    )
    ap.add_argument(
        "--ga-eval-workers",
        type=int,
        default=1,
        help="Thread pool size for GA fitness eval (isolated clones when >1).",
    )
    args = ap.parse_args()

    nb_paths = _parse_neighbor_bundle_paths(args.neighbor_json_list) if args.neighbor_json_list else None
    if nb_paths is None:
        nb_weights = None
    elif args.neighbor_weights_json_list:
        nb_weights = _parse_neighbor_weights_bundle(args.neighbor_weights_json_list, len(nb_paths))
    else:
        nb_weights = None

    if nb_paths is None:
        seeds = [int(x.strip()) for x in args.graph_seeds.split(",") if x.strip()]
        if not seeds:
            raise SystemExit("Provide at least one --graph-seeds value (or use --neighbor-json-list).")

    ga_budget_1d = bool(args.ga_budget_sweep)
    ga_budget_2d = bool(args.ga_budget_2d)
    ga_budget_pop_1d = bool(args.ga_population_sweep)
    modes = [ga_budget_1d, ga_budget_2d, ga_budget_pop_1d]
    if sum(1 for m in modes if m) > 1:
        raise SystemExit("Pick at most one of --ga-budget-sweep, --ga-budget-2d, --ga-population-sweep.")
    ga_budget = ga_budget_1d or ga_budget_2d or ga_budget_pop_1d
    gw: list[int] | None = None
    pw: list[int] | None = None
    if ga_budget_1d:
        if not args.ga_generations_values:
            raise SystemExit("--ga-budget-sweep requires --ga-generations-values.")
        gw = [int(x.strip()) for x in str(args.ga_generations_values).split(",") if x.strip()]
        if not gw:
            raise SystemExit("--ga-generations-values must list at least one int.")
    elif ga_budget_2d:
        if not args.ga_generations_values or not args.ga_population_values:
            raise SystemExit("--ga-budget-2d requires --ga-generations-values and --ga-population-values.")
        gw = [int(x.strip()) for x in str(args.ga_generations_values).split(",") if x.strip()]
        pw = [int(x.strip()) for x in str(args.ga_population_values).split(",") if x.strip()]
        if not gw:
            raise SystemExit("--ga-generations-values must list at least one int.")
        if not pw:
            raise SystemExit("--ga-population-values must list at least one int.")
    elif ga_budget_pop_1d:
        if not args.ga_population_values:
            raise SystemExit("--ga-population-sweep requires --ga-population-values.")
        pw = [int(x.strip()) for x in str(args.ga_population_values).split(",") if x.strip()]
        if not pw:
            raise SystemExit("--ga-population-values must list at least one int.")
        if any(p < 2 for p in pw):
            raise SystemExit("--ga-population-values entries must be >= 2.")
        if int(args.ga_fixed_generations) < 1:
            raise SystemExit("--ga-fixed-generations must be >= 1.")

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

    if ga_budget and (sweep_1 or sweep_2_axis):
        raise SystemExit("Use either GA budget modes or physics (--sweep-param) sweeps, not both.")

    topo = str(args.topology)
    common = dict(
        graph_kind=str(args.graph_kind),
        nodes=int(args.nodes),
        graph_seeds=seeds if nb_paths is None else [0],
        rollout_seed=int(args.rollout_seed),
        er_p=float(args.er_p),
        ws_k=int(args.ws_k),
        ws_p=float(args.ws_p),
        base_panic=float(args.base_panic),
        contagion_beta=float(args.beta),
        whale_frac=float(args.whale_frac),
        max_steps=int(args.max_steps),
        topology_representation=topo,
        neighbor_json_paths=nb_paths,
        neighbor_weights_json_paths=nb_weights,
    )

    if ga_budget_1d:
        assert gw is not None
        payload = robustness_ga_generations_1d_sweep(
            ga_generations_values=gw,
            population_size=int(args.ga_population_size),
            ga_seed=int(args.ga_seed),
            horizon=int(args.horizon),
            rollout_seed=int(args.rollout_seed),
            base_panic=float(args.base_panic),
            graph_kind=str(args.graph_kind),
            nodes=int(args.nodes),
            graph_seeds=seeds if nb_paths is None else None,
            train_graph_seed=args.train_graph_seed,
            er_p=float(args.er_p),
            ws_k=int(args.ws_k),
            ws_p=float(args.ws_p),
            contagion_beta=float(args.beta),
            whale_frac=float(args.whale_frac),
            max_steps=int(args.max_steps),
            topology_representation=topo,
            neighbor_json_paths=nb_paths,
            neighbor_weights_json_paths=nb_weights,
            eval_workers=int(args.ga_eval_workers),
        )
    elif ga_budget_pop_1d:
        assert pw is not None
        payload = robustness_ga_population_1d_sweep(
            ga_population_sizes=pw,
            ga_generations_fixed=int(args.ga_fixed_generations),
            ga_seed=int(args.ga_seed),
            horizon=int(args.horizon),
            rollout_seed=int(args.rollout_seed),
            base_panic=float(args.base_panic),
            graph_kind=str(args.graph_kind),
            nodes=int(args.nodes),
            graph_seeds=seeds if nb_paths is None else None,
            train_graph_seed=args.train_graph_seed,
            er_p=float(args.er_p),
            ws_k=int(args.ws_k),
            ws_p=float(args.ws_p),
            contagion_beta=float(args.beta),
            whale_frac=float(args.whale_frac),
            max_steps=int(args.max_steps),
            topology_representation=topo,
            neighbor_json_paths=nb_paths,
            neighbor_weights_json_paths=nb_weights,
            eval_workers=int(args.ga_eval_workers),
        )
    elif ga_budget_2d:
        assert gw is not None and pw is not None
        payload = robustness_ga_budget_2d_grid(
            ga_generations_values=gw,
            ga_population_sizes=pw,
            ga_seed=int(args.ga_seed),
            horizon=int(args.horizon),
            rollout_seed=int(args.rollout_seed),
            base_panic=float(args.base_panic),
            graph_kind=str(args.graph_kind),
            nodes=int(args.nodes),
            graph_seeds=seeds if nb_paths is None else None,
            train_graph_seed=args.train_graph_seed,
            er_p=float(args.er_p),
            ws_k=int(args.ws_k),
            ws_p=float(args.ws_p),
            contagion_beta=float(args.beta),
            whale_frac=float(args.whale_frac),
            max_steps=int(args.max_steps),
            topology_representation=topo,
            neighbor_json_paths=nb_paths,
            neighbor_weights_json_paths=nb_weights,
            eval_workers=int(args.ga_eval_workers),
        )
    elif args.sweep_param is not None and args.sweep_param_2 is not None:
        vx = [float(x.strip()) for x in str(args.sweep_values).split(",") if x.strip()]
        vy = [float(x.strip()) for x in str(args.sweep_values_2).split(",") if x.strip()]
        if not vx or not vy:
            raise SystemExit("Both sweep value lists must have at least one number.")
        rng = np.random.default_rng(int(args.genome_seed))
        genome = rng.uniform(size=(int(args.horizon), 2))
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
        rng = np.random.default_rng(int(args.genome_seed))
        genome = rng.uniform(size=(int(args.horizon), 2))
        payload = robustness_ensemble_1d_param_sweep(
            genome,
            sweep_param=str(args.sweep_param),
            sweep_values=sweep_vals,
            **common,
        )
    elif nb_paths is not None:
        rng = np.random.default_rng(int(args.genome_seed))
        genome = rng.uniform(size=(int(args.horizon), 2))
        payload = robustness_rollouts_neighbor_json_bundle(
            genome,
            neighbor_json_paths=nb_paths,
            rollout_seed=int(args.rollout_seed),
            contagion_beta=float(args.beta),
            whale_frac=float(args.whale_frac),
            base_panic=float(args.base_panic),
            max_steps=int(args.max_steps),
            neighbor_weights_json_paths=nb_weights,
        )
    else:
        rng = np.random.default_rng(int(args.genome_seed))
        genome = rng.uniform(size=(int(args.horizon), 2))
        synthetic_kw = {k: v for k, v in common.items() if k not in _SYNTHETIC_ONLY_KEYS}
        payload = robustness_rollouts_over_graph_seeds(genome, **synthetic_kw)

    if ga_budget:
        payload["genome_seed"] = None
    else:
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
        elif sch == "fragility-robustness-ga-budget-1d-v1":
            for pt in payload["points"]:
                s = pt["ensemble"]["summary"]
                print(
                    f"ga_generations={pt['ga_generations']} "
                    f"best_fitness={pt['ga_best_fitness']:.5f} "
                    f"collapse_rate={s['collapse_rate']:.3f} "
                    f"integral_p50={s['integral_instability_p50']:.6f}"
                )
            sp = payload["summary"]
            print(
                f"--- GA budget steps={sp['steps']} collapse_rate in "
                f"[{sp['collapse_rate_min']:.3f}, {sp['collapse_rate_max']:.3f}] "
                f"spread={sp['collapse_rate_spread']:.3f}"
            )
        elif sch == "fragility-robustness-ga-population-1d-v1":
            for pt in payload["points"]:
                s = pt["ensemble"]["summary"]
                print(
                    f"population_size={pt['population_size']} "
                    f"best_fitness={pt['ga_best_fitness']:.5f} "
                    f"collapse_rate={s['collapse_rate']:.3f} "
                    f"integral_p50={s['integral_instability_p50']:.6f}"
                )
            sp = payload["summary"]
            print(
                f"--- GA population sweep steps={sp['steps']} collapse_rate in "
                f"[{sp['collapse_rate_min']:.3f}, {sp['collapse_rate_max']:.3f}] "
                f"spread={sp['collapse_rate_spread']:.3f}"
            )
        elif sch == "fragility-robustness-ga-budget-2d-v1":
            for pt in payload["points"]:
                s = pt["ensemble"]["summary"]
                print(
                    f"gen={pt['ga_generations']} pop={pt['population_size']} "
                    f"best_fitness={pt['ga_best_fitness']:.5f} "
                    f"collapse_rate={s['collapse_rate']:.3f} "
                    f"integral_p50={s['integral_instability_p50']:.6f}"
                )
            sp = payload["summary"]
            print(
                f"--- GA 2D grid cells={sp['grid_cells']} collapse_rate in "
                f"[{sp['collapse_rate_min']:.3f}, {sp['collapse_rate_max']:.3f}] "
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
