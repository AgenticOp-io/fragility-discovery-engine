"""Regenerate checked-in JSON under artifacts/ from pinned bundles and small CLIs.

Not run by pytest. Safe to re-run after changing GOLDEN_METRICS or replay schema.

  python scripts/regenerate_bundled_viewer_samples.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from fragility_engine.benchmarks.suite import BUNDLE_IDS, run_bundle_rollout_once
from fragility_engine.explain.interaction_summary import summarize_attribution_merge
from fragility_engine.runner import rollout_to_replay_dict

ROOT = Path(__file__).resolve().parents[1]
REPLAY_VIEWER = ROOT / "artifacts" / "replay_viewer"
ATTRIBUTION_VIEWER = ROOT / "artifacts" / "attribution_viewer"
COMPOSITE_DEMO = ROOT / "artifacts" / "composite_demo"
FLAGSHIP_BUNDLED = ROOT / "artifacts" / "flagship" / "bundled"

_REPLAY_BUNDLE_MAP = {
    "sample_replay.json": "aggregate_rollout_v1",
    "sample_network_replay.json": "network_er_rollout_v1",
    "sample_resource_cascade_replay.json": "resource_cascade_rollout_v1",
    "sample_service_backlog_replay.json": "service_backlog_rollout_v1",
}


def _write_replay_samples() -> None:
    REPLAY_VIEWER.mkdir(parents=True, exist_ok=True)
    for filename, bundle_id in _REPLAY_BUNDLE_MAP.items():
        r = run_bundle_rollout_once(bundle_id)
        payload = rollout_to_replay_dict(r)
        out = REPLAY_VIEWER / filename
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}  integral={payload['integral_instability']:.6f}")


def _write_attribution_samples(py: str) -> None:
    ATTRIBUTION_VIEWER.mkdir(parents=True, exist_ok=True)
    joint = ATTRIBUTION_VIEWER / "sample_attribution_merge_resource_cascade.json"
    subprocess.run(
        [
            py,
            str(ROOT / "scripts" / "export_resource_cascade_joint_attribution.py"),
            "--out",
            str(joint),
            "--horizon",
            "10",
            "--seed",
            "66201",
            "--genome-seed",
            "66202",
            "--initial-overload",
            "0.07",
        ],
        check=True,
        cwd=str(ROOT),
    )
    print(f"wrote {joint.relative_to(ROOT)}")
    triple = ATTRIBUTION_VIEWER / "sample_attribution_merge_resource_cascade_triple.json"
    subprocess.run(
        [
            py,
            str(ROOT / "scripts" / "export_resource_cascade_triple_attribution.py"),
            "--out",
            str(triple),
            "--horizon",
            "10",
            "--seed",
            "66203",
            "--genome-seed",
            "66204",
            "--initial-overload",
            "0.07",
            "--variant-initial-overload",
            "0.11",
            "--variant-cascade-coupling",
            "0.35",
            "--remove",
            "0",
        ],
        check=True,
        cwd=str(ROOT),
    )
    print(f"wrote {triple.relative_to(ROOT)}")
    summary_path = ATTRIBUTION_VIEWER / "sample_triple_interaction_summary.json"
    merge = json.loads(triple.read_text(encoding="utf-8"))
    summary_path.write_text(
        json.dumps(summarize_attribution_merge(merge), indent=2),
        encoding="utf-8",
    )
    print(f"wrote {summary_path.relative_to(ROOT)}")


def _write_network_chain_sample(py: str) -> None:
    ATTRIBUTION_VIEWER.mkdir(parents=True, exist_ok=True)
    nl_path = ATTRIBUTION_VIEWER / "_regen_neighbor_list.json"
    nl_path.write_text("[[1],[0]]", encoding="utf-8")
    chain_path = ROOT / "tests" / "fixtures" / "chains" / "network_contagion_base_panic_chain.json"
    out = ATTRIBUTION_VIEWER / "sample_network_chain_contagion_base_panic.json"
    subprocess.run(
        [
            py,
            str(ROOT / "scripts" / "export_counterfactual_chain.py"),
            "--chain-json",
            str(chain_path),
            "--neighbor-json",
            str(nl_path),
            "--horizon",
            "10",
            "--seed",
            "66501",
            "--genome-seed",
            "66502",
            "--base-panic",
            "0.05",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    print(f"wrote {out.relative_to(ROOT)}")
    try:
        nl_path.unlink()
    except OSError:
        pass


def _write_composite_samples(py: str) -> None:
    COMPOSITE_DEMO.mkdir(parents=True, exist_ok=True)
    triple = COMPOSITE_DEMO / "sample_triple_composite.json"
    subprocess.run(
        [
            py,
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--triple",
            "--horizon",
            "10",
            "--genome-seed",
            "334",
            "--graph-seed",
            "56",
            "--aggregate-seed",
            "7100",
            "--network-seed",
            "7101",
            "--cascade-seed",
            "7102",
            "--out",
            str(triple),
        ],
        check=True,
        cwd=str(ROOT),
    )
    print(f"wrote {triple.relative_to(ROOT)}")
    quad = COMPOSITE_DEMO / "sample_quad_composite.json"
    subprocess.run(
        [
            py,
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--quad",
            "--horizon",
            "10",
            "--genome-seed",
            "333",
            "--graph-seed",
            "55",
            "--aggregate-seed",
            "7000",
            "--network-seed",
            "7001",
            "--cascade-seed",
            "7002",
            "--backlog-seed",
            "7003",
            "--out",
            str(quad),
        ],
        check=True,
        cwd=str(ROOT),
    )
    print(f"wrote {quad.relative_to(ROOT)}")


def _write_aggregate_chain_sample(py: str) -> None:
    ATTRIBUTION_VIEWER.mkdir(parents=True, exist_ok=True)
    chain_path = ROOT / "tests" / "fixtures" / "chains" / "aggregate_panic_depeg_chain.json"
    out = ATTRIBUTION_VIEWER / "sample_aggregate_chain_rumor_depeg.json"
    subprocess.run(
        [
            py,
            str(ROOT / "scripts" / "export_aggregate_counterfactual_chain.py"),
            "--chain-json",
            str(chain_path),
            "--horizon",
            "10",
            "--seed",
            "66601",
            "--genome-seed",
            "66602",
            "--initial-panic",
            "0.05",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    print(f"wrote {out.relative_to(ROOT)}")


def _write_service_backlog_chain_sample(py: str) -> None:
    ATTRIBUTION_VIEWER.mkdir(parents=True, exist_ok=True)
    chain_path = ROOT / "tests" / "fixtures" / "chains" / "service_backlog_process_ingest_chain.json"
    out = ATTRIBUTION_VIEWER / "sample_service_backlog_chain_process_ingest.json"
    subprocess.run(
        [
            py,
            str(ROOT / "scripts" / "export_service_backlog_counterfactual_chain.py"),
            "--chain-json",
            str(chain_path),
            "--horizon",
            "10",
            "--seed",
            "66701",
            "--genome-seed",
            "66702",
            "--initial-backlog",
            "0.065",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    print(f"wrote {out.relative_to(ROOT)}")


def _write_flagship_bundled() -> None:
    from fragility_engine.benchmarks.flagship import run_flagship_demo

    FLAGSHIP_BUNDLED.mkdir(parents=True, exist_ok=True)
    run_flagship_demo(
        FLAGSHIP_BUNDLED,
        validate_bundles_first=False,
        horizon=10,
        generations=2,
        population_size=8,
        ga_seed=424_242,
        max_steps=28,
        eval_workers=1,
    )
    rel = FLAGSHIP_BUNDLED.relative_to(ROOT)
    print(f"wrote {rel} (best_replay.json, pareto_front.json, fragility_certificate.json)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-attribution", action="store_true", help="Skip attribution-merge sample.")
    ap.add_argument("--skip-composite", action="store_true", help="Skip quad composite sample.")
    ap.add_argument("--skip-flagship", action="store_true", help="Skip flagship bundled GA artifacts.")
    args = ap.parse_args()
    py = sys.executable
    _write_replay_samples()
    if not args.skip_attribution:
        _write_attribution_samples(py)
        _write_network_chain_sample(py)
        _write_aggregate_chain_sample(py)
        _write_service_backlog_chain_sample(py)
    if not args.skip_composite:
        _write_composite_samples(py)
    if not args.skip_flagship:
        _write_flagship_bundled()
    print(f"OK: regenerated bundled viewer samples ({len(BUNDLE_IDS)} replay bundles)")


if __name__ == "__main__":
    main()
