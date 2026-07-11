"""``fragility`` CLI — search, minimize, replay, certify, check-world, falsify (Phases R/S)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine import __version__
from fragility_engine.adversary.encoding import decode_schedule
from fragility_engine.adversary.search import genetic_search, monte_carlo_search
from fragility_engine.byow.check import check_rollout_determinism
from fragility_engine.byow.examples import get_example as get_byow_example
from fragility_engine.byow.examples import list_examples as list_byow_examples
from fragility_engine.explain.minimal_collapse import minimize_schedule_with_rollout
from fragility_engine.falsify.examples import get_example as get_falsify_example
from fragility_engine.falsify.examples import list_examples as list_falsify_examples
from fragility_engine.falsify.rollout import replay_meta_for_falsification
from fragility_engine.runner import rollout_to_replay_dict, summarize_findings


def _build_byow_evaluator(example_name: str):
    spec = get_byow_example(example_name)
    world = spec.make_world()

    def evaluator(genome: np.ndarray, seed: int):
        return spec.rollout(world, genome, seed)

    return spec, evaluator


def _build_falsify_evaluator(example_name: str):
    spec = get_falsify_example(example_name)
    world = spec.make_world()

    def evaluator(genome: np.ndarray, seed: int):
        return spec.rollout(world, genome, seed)

    return spec, evaluator


def _write_replay(result, path: Path, *, meta: dict) -> None:
    replay = rollout_to_replay_dict(result)
    replay["meta"] = meta
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(replay, indent=2), encoding="utf-8")


def cmd_search(args: argparse.Namespace) -> int:
    spec, evaluator = _build_byow_evaluator(args.example)
    horizon = int(args.horizon or spec.default_horizon)
    if args.method == "ga":
        search = genetic_search(
            evaluator,
            horizon=horizon,
            generations=int(args.generations),
            population_size=int(args.population_size),
            seed=int(args.seed),
        )
    else:
        search = monte_carlo_search(
            evaluator,
            horizon=horizon,
            samples=int(args.samples),
            seed=int(args.seed),
        )
    print(summarize_findings(search.best_rollout))
    if args.export_replay:
        _write_replay(
            search.best_rollout,
            Path(args.export_replay),
            meta={"cli": "fragility search", "example": spec.name, "harness_kind": "dynamics_v1"},
        )
        print(f"wrote {args.export_replay}")
    if args.export_genome:
        Path(args.export_genome).write_text(json.dumps(search.best_genome.tolist()), encoding="utf-8")
        print(f"wrote genome {args.export_genome}")
    return 0


def cmd_minimize(args: argparse.Namespace) -> int:
    spec, evaluator = _build_byow_evaluator(args.example)
    if args.genome_file:
        genome = np.array(json.loads(Path(args.genome_file).read_text(encoding="utf-8")), dtype=np.float64)
    else:
        horizon = int(args.horizon or spec.default_horizon)
        search = genetic_search(
            evaluator,
            horizon=horizon,
            generations=int(args.generations),
            population_size=int(args.population_size),
            seed=int(args.seed),
        )
        genome = search.best_genome
        print("=== search (for minimize input) ===")
        print(summarize_findings(search.best_rollout))

    report, min_rollout = minimize_schedule_with_rollout(genome, evaluator, base_seed=int(args.base_seed))
    print(json.dumps({k: v for k, v in report.items() if k != "minimal_genome"}, indent=2))
    if min_rollout and args.export_replay:
        _write_replay(
            min_rollout,
            Path(args.export_replay),
            meta={"cli": "fragility minimize", "example": spec.name, "harness_kind": "dynamics_v1"},
        )
        print(f"wrote {args.export_replay}")
    return 0 if min_rollout is not None else 1


def cmd_replay(args: argparse.Namespace) -> int:
    path = Path(args.input)
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"schema_version", "simulation_mode", "trajectory", "collapsed"}
    missing = required - set(data)
    if missing:
        print(f"invalid replay: missing keys {sorted(missing)}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "simulation_mode": data["simulation_mode"],
                "collapsed": data["collapsed"],
                "steps": len(data["trajectory"]),
                "meta": data.get("meta", {}),
            },
            indent=2,
        )
    )
    return 0


def cmd_certify(args: argparse.Namespace) -> int:
    from fragility_engine.benchmarks.flagship import run_flagship_demo

    out = Path(args.out_dir)
    result = run_flagship_demo(
        out,
        validate_bundles_first=not args.skip_validate,
        horizon=int(args.horizon),
        generations=int(args.generations),
        population_size=int(args.population_size),
    )
    payload = {
        "output_dir": str(out),
        "certificate_sha256": result["certificate"].get("certificate_content_sha256"),
    }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_check_world(args: argparse.Namespace) -> int:
    spec, evaluator = _build_byow_evaluator(args.example)
    ok, msg = check_rollout_determinism(evaluator, seed=int(args.seed))
    print(msg)
    return 0 if ok else 1


def cmd_falsify_search(args: argparse.Namespace) -> int:
    spec, evaluator = _build_falsify_evaluator(args.example)
    horizon = int(args.horizon or spec.default_horizon)
    search = genetic_search(
        evaluator,
        horizon=horizon,
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
    )
    print(summarize_findings(search.best_rollout))
    print("decoded shocks:")
    for t, events in sorted(decode_schedule(search.best_genome).items()):
        for e in events:
            print(f"  t={t:>2}  {e.kind:<12} mag={e.magnitude:.3f}")

    report, min_rollout = minimize_schedule_with_rollout(search.best_genome, evaluator, base_seed=int(args.base_seed))
    if min_rollout is not None:
        kept = report.get("minimal_events_by_timestep", {})
        print(f"minimized: {len(kept)} timesteps still violate claim")

    out = Path(args.export_replay) if args.export_replay else None
    if out and search.best_rollout.collapsed:
        meta = {"cli": "fragility falsify search", **replay_meta_for_falsification(example=spec.name)}
        _write_replay(search.best_rollout, out, meta=meta)
        print(f"wrote {out}")
    return 0 if search.best_rollout.collapsed else 1


def cmd_examples(_args: argparse.Namespace) -> int:
    print("BYOW examples:", ", ".join(list_byow_examples()))
    print("Falsification examples:", ", ".join(list_falsify_examples()))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fragility", description="Fragility Discovery Engine CLI")
    p.add_argument("--version", action="version", version=f"fragility-engine {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    ex = sub.add_parser("examples", help="List installable tutorial examples")
    ex.set_defaults(func=cmd_examples)

    sp = sub.add_parser("search", help="GA or MC search on a BYOW tutorial example")
    sp.add_argument("--example", default="capacity-pool")
    sp.add_argument("--method", choices=("ga", "mc"), default="ga")
    sp.add_argument("--generations", type=int, default=10)
    sp.add_argument("--population-size", type=int, default=20)
    sp.add_argument("--samples", type=int, default=40)
    sp.add_argument("--horizon", type=int, default=None)
    sp.add_argument("--seed", type=int, default=411)
    sp.add_argument("--export-replay", type=Path, default=None)
    sp.add_argument("--export-genome", type=Path, default=None)
    sp.set_defaults(func=cmd_search)

    mp = sub.add_parser("minimize", help="Greedy minimal failing schedule")
    mp.add_argument("--example", default="capacity-pool")
    mp.add_argument("--genome-file", type=Path, default=None)
    mp.add_argument("--generations", type=int, default=10)
    mp.add_argument("--population-size", type=int, default=20)
    mp.add_argument("--horizon", type=int, default=None)
    mp.add_argument("--seed", type=int, default=411)
    mp.add_argument("--base-seed", type=int, default=515151)
    mp.add_argument("--export-replay", type=Path, default=None)
    mp.set_defaults(func=cmd_minimize)

    rp = sub.add_parser("replay", help="Validate a replay JSON file")
    rp.add_argument("input", type=Path)
    rp.set_defaults(func=cmd_replay)

    cp = sub.add_parser("certify", help="Run flagship demo and write fragility-certificate-v1 bundle")
    cp.add_argument("--out-dir", type=Path, default=Path("artifacts/flagship/output"))
    cp.add_argument("--skip-validate", action="store_true")
    cp.add_argument("--horizon", type=int, default=14)
    cp.add_argument("--generations", type=int, default=3)
    cp.add_argument("--population-size", type=int, default=12)
    cp.set_defaults(func=cmd_certify)

    ck = sub.add_parser("check-world", help="Determinism check on a BYOW example")
    ck.add_argument("--example", default="capacity-pool")
    ck.add_argument("--seed", type=int, default=9001)
    ck.set_defaults(func=cmd_check_world)

    fs = sub.add_parser("falsify", help="Falsification harness commands")
    fs_sub = fs.add_subparsers(dest="falsify_cmd", required=True)
    fsearch = fs_sub.add_parser("search", help="Search for schedules that violate an invariant")
    fsearch.add_argument("--example", default="ranked-store")
    fsearch.add_argument("--generations", type=int, default=12)
    fsearch.add_argument("--population-size", type=int, default=24)
    fsearch.add_argument("--horizon", type=int, default=None)
    fsearch.add_argument("--seed", type=int, default=707)
    fsearch.add_argument("--base-seed", type=int, default=515151)
    fsearch.add_argument("--export-replay", type=Path, default=None)
    fsearch.set_defaults(func=cmd_falsify_search)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
