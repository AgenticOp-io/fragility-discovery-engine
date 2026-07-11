"""``fragility`` CLI - search, illuminate, differential, evidence-pack, certify, falsify, shorthand."""

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


def cmd_shorthand(args: argparse.Namespace) -> int:
    from fragility_engine.shorthand import list_capsules, resolve_task
    from fragility_engine.shorthand.resolve import export_corpus

    if args.shorthand_cmd == "list":
        for tid in list_capsules():
            r = resolve_task(tid)
            assert r.capsule is not None
            print(f"{tid}\t{r.tier}\t{r.capsule.summary}")
        return 0
    if args.shorthand_cmd == "resolve":
        r = resolve_task(args.task, needs_prose=bool(args.needs_prose))
        print(json.dumps(r.to_dict(), indent=2))
        return 0 if r.found else 1
    if args.shorthand_cmd == "export":
        out = Path(args.out)
        corpus = export_corpus()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(corpus, indent=2), encoding="utf-8")
        print(f"wrote {out}")
        return 0
    return 1


def cmd_illuminate(args: argparse.Namespace) -> int:
    from fragility_engine.adversary.scenario_archive import quality_diversity_search, scenario_archive_payload

    spec, evaluator = _build_byow_evaluator(args.example)
    horizon = int(args.horizon or spec.default_horizon)
    qd = quality_diversity_search(
        evaluator,
        horizon=horizon,
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
    )
    print(summarize_findings(qd.search.best_rollout))
    print(f"niches illuminated: {len(qd.niches)}")
    if args.export_archive:
        out = Path(args.export_archive)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(scenario_archive_payload(qd), indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    if args.export_replay:
        _write_replay(
            qd.search.best_rollout,
            Path(args.export_replay),
            meta={"cli": "fragility illuminate", "example": spec.name, "harness_kind": "dynamics_v1"},
        )
        print(f"wrote {args.export_replay}")
    return 0


def cmd_differential(args: argparse.Namespace) -> int:
    from fragility_engine.adversary.differential import differential_search, differential_stress_payload

    spec_a, eval_a = _build_byow_evaluator(args.example_a)
    spec_b, eval_b = _build_byow_evaluator(args.example_b)
    horizon = int(args.horizon or max(spec_a.default_horizon, spec_b.default_horizon))
    _result, diff = differential_search(
        eval_a,
        eval_b,
        horizon=horizon,
        seed=int(args.seed),
        method=str(args.method),
        generations=int(args.generations),
        population_size=int(args.population_size),
        samples=int(args.samples),
    )
    payload = differential_stress_payload(diff, world_a=spec_a.name, world_b=spec_b.name)
    print(json.dumps({k: v for k, v in payload.items() if k != "genome"}, indent=2))
    if args.export_json:
        out = Path(args.export_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    if args.export_replay:
        _write_replay(
            diff.rollout_a,
            Path(args.export_replay),
            meta={
                "cli": "fragility differential",
                "example_a": spec_a.name,
                "example_b": spec_b.name,
                "harness_kind": "differential_stress_v1",
            },
        )
        print(f"wrote {args.export_replay}")
    return 0


def cmd_plausible(args: argparse.Namespace) -> int:
    from fragility_engine.adversary.plausibility import plausibility_search_payload, plausible_search

    spec, evaluator = _build_byow_evaluator(args.example)
    horizon = int(args.horizon or spec.default_horizon)
    psr = plausible_search(
        evaluator,
        horizon=horizon,
        seed=int(args.seed),
        plausibility_weight=float(args.plausibility_weight),
        method=str(args.method),
        generations=int(args.generations),
        population_size=int(args.population_size),
        samples=int(args.samples),
    )
    payload = plausibility_search_payload(psr)
    print(summarize_findings(psr.search.best_rollout))
    print(
        json.dumps(
            {
                "insanity_budget": payload["insanity_budget"],
                "log_likelihood": payload["log_likelihood"],
                "plausibility_weight": payload["plausibility_weight"],
                "active_shock_events": payload["active_shock_events"],
            },
            indent=2,
        )
    )
    if args.export_json:
        out = Path(args.export_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    if args.export_replay:
        _write_replay(
            psr.search.best_rollout,
            Path(args.export_replay),
            meta={
                "cli": "fragility plausible-search",
                "example": spec.name,
                "harness_kind": "plausibility_search_v1",
            },
        )
        print(f"wrote {args.export_replay}")
    return 0


def cmd_falsify_stl(args: argparse.Namespace) -> int:
    from fragility_engine.falsify.stl import stl_falsify_search, stl_robustness_payload

    if args.example:
        spec, evaluator = _build_falsify_evaluator(args.example)
        horizon = int(args.horizon or spec.default_horizon)
        example_name = spec.name
        harness = "falsification_v1"
    else:
        spec, evaluator = _build_byow_evaluator(args.byow_example)
        horizon = int(args.horizon or spec.default_horizon)
        example_name = spec.name
        harness = "dynamics_v1"

    res = stl_falsify_search(
        evaluator,
        str(args.formula),
        horizon=horizon,
        seed=int(args.seed),
        generations=int(args.generations),
        population_size=int(args.population_size),
    )
    payload = stl_robustness_payload(res)
    print(json.dumps({k: v for k, v in payload.items() if k != "genome"}, indent=2))
    if args.export_json:
        out = Path(args.export_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    if args.export_replay and res.search.best_rollout.trajectory:
        _write_replay(
            res.search.best_rollout,
            Path(args.export_replay),
            meta={
                "cli": "fragility falsify stl",
                "example": example_name,
                "formula": args.formula,
                "harness_kind": harness,
            },
        )
        print(f"wrote {args.export_replay}")
    return 0 if res.violated else 1


def cmd_evidence_pack(args: argparse.Namespace) -> int:
    from fragility_engine.benchmarks.evidence_pack import build_evidence_pack

    paths = [Path(p) for p in (args.artifact or [])]
    pack = build_evidence_pack(
        artifact_paths=paths or None,
        include_benchmark_manifest=not args.no_manifest,
        activity_label=str(args.activity),
        notes=str(args.notes or ""),
        repo_root=Path.cwd(),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    summary = {
        "out": str(out),
        "pack_content_sha256": pack["pack_content_sha256"],
        "entities": len(pack["entities"]),
    }
    print(json.dumps(summary, indent=2))
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
    fstl = fs_sub.add_parser("stl", help="Falsify a discrete-time STL formula (robustness search)")
    fstl.add_argument(
        "--formula",
        required=True,
        help='e.g. "G[0,10] x[0] < 0.9" or "F[0,8] x[1] > 0.5"',
    )
    fstl.add_argument("--example", default=None, help="Falsification example (ranked-store)")
    fstl.add_argument("--byow-example", default="capacity-pool", help="BYOW example if --example omitted")
    fstl.add_argument("--generations", type=int, default=10)
    fstl.add_argument("--population-size", type=int, default=20)
    fstl.add_argument("--horizon", type=int, default=None)
    fstl.add_argument("--seed", type=int, default=808)
    fstl.add_argument("--export-json", type=Path, default=None)
    fstl.add_argument("--export-replay", type=Path, default=None)
    fstl.set_defaults(func=cmd_falsify_stl)

    ill = sub.add_parser(
        "illuminate",
        help="Quality-diversity search -> scenario-archive-v1 (MAP-Elites niches)",
    )
    ill.add_argument("--example", default="capacity-pool")
    ill.add_argument("--generations", type=int, default=6)
    ill.add_argument("--population-size", type=int, default=16)
    ill.add_argument("--horizon", type=int, default=None)
    ill.add_argument("--seed", type=int, default=511)
    ill.add_argument("--export-archive", type=Path, default=None)
    ill.add_argument("--export-replay", type=Path, default=None)
    ill.set_defaults(func=cmd_illuminate)

    diff = sub.add_parser(
        "differential",
        help="Find schedules that break example A but not B (differential-stress-v1)",
    )
    diff.add_argument("--example-a", default="capacity-pool")
    diff.add_argument("--example-b", default="token-bucket")
    diff.add_argument("--method", choices=("ga", "mc"), default="ga")
    diff.add_argument("--generations", type=int, default=8)
    diff.add_argument("--population-size", type=int, default=16)
    diff.add_argument("--samples", type=int, default=40)
    diff.add_argument("--horizon", type=int, default=None)
    diff.add_argument("--seed", type=int, default=909)
    diff.add_argument("--export-json", type=Path, default=None)
    diff.add_argument("--export-replay", type=Path, default=None)
    diff.set_defaults(func=cmd_differential)

    pl = sub.add_parser(
        "plausible-search",
        help="Severity vs insanity-budget search (plausibility-search-v1)",
    )
    pl.add_argument("--example", default="capacity-pool")
    pl.add_argument("--method", choices=("ga", "mc"), default="ga")
    pl.add_argument("--plausibility-weight", type=float, default=0.35)
    pl.add_argument("--generations", type=int, default=8)
    pl.add_argument("--population-size", type=int, default=16)
    pl.add_argument("--samples", type=int, default=40)
    pl.add_argument("--horizon", type=int, default=None)
    pl.add_argument("--seed", type=int, default=616)
    pl.add_argument("--export-json", type=Path, default=None)
    pl.add_argument("--export-replay", type=Path, default=None)
    pl.set_defaults(func=cmd_plausible)

    ep = sub.add_parser(
        "evidence-pack",
        help="Build evidence-pack-v1 (PROV-lite) around digests + certificate",
    )
    ep.add_argument("--out", type=Path, required=True)
    ep.add_argument("--artifact", action="append", default=[], help="JSON artifact path (repeatable)")
    ep.add_argument("--activity", default="fragility_evidence_assembly")
    ep.add_argument("--notes", default="")
    ep.add_argument("--no-manifest", action="store_true")
    ep.set_defaults(func=cmd_evidence_pack)

    sh = sub.add_parser(
        "shorthand",
        help="Operator Intelligence Shorthand (resolve verified recipes; no LLM in-sim)",
    )
    sh_sub = sh.add_subparsers(dest="shorthand_cmd", required=True)
    sh_list = sh_sub.add_parser("list", help="List curated operator capsules")
    sh_list.set_defaults(func=cmd_shorthand)
    sh_res = sh_sub.add_parser("resolve", help="Resolve a task_id to tier + verify command")
    sh_res.add_argument("task", help="Capsule task id (e.g. validate-benchmarks)")
    sh_res.add_argument(
        "--needs-prose",
        action="store_true",
        help="Force IS-T1+ path (post-hoc narration only)",
    )
    sh_res.set_defaults(func=cmd_shorthand)
    sh_exp = sh_sub.add_parser("export", help="Export shorthand corpus JSON")
    sh_exp.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/operator_shorthand/fde-shorthands.v1.json"),
    )
    sh_exp.set_defaults(func=cmd_shorthand)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
