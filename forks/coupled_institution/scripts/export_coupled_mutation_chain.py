#!/usr/bin/env python3
"""Export coupled fork mutation-chain attribution JSON (path trace + baseline/final)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coupled_institution.golden import _load_fixture, _schedule_from_fixture  # noqa: E402
from coupled_institution.mutation_chain import (  # noqa: E402
    CHAIN_SPEC_SCHEMA,
    build_chain_attribution_bundle,
    mutation_chain_path_rollouts,
    parse_chain_spec,
)

DEFAULT_CHAIN = ROOT / "tests" / "fixtures" / "coupling_chain.json"


def main() -> None:
    p = argparse.ArgumentParser(description="Coupled institution mutation chain export.")
    p.add_argument("--chain-json", type=Path, default=DEFAULT_CHAIN)
    p.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts" / "sample_coupled_mutation_chain.json",
    )
    p.add_argument("--base-coupling", type=float, default=None, help="Default: fixture coupling_strength.")
    args = p.parse_args()

    raw_spec = json.loads(args.chain_json.read_text(encoding="utf-8"))
    steps = parse_chain_spec(raw_spec)
    fix = _load_fixture()
    schedule = _schedule_from_fixture(fix)
    seed = int(fix["rollout_seed"])
    base_c = float(args.base_coupling if args.base_coupling is not None else fix["coupling_strength"])

    rollouts = mutation_chain_path_rollouts(
        schedule,
        base_coupling=base_c,
        steps=steps,
        seed=seed,
    )
    payload = build_chain_attribution_bundle(
        rollouts,
        steps,
        rollout_seed=seed,
        baseline_coupling=base_c,
    )
    payload["meta"] = {
        "cli": "export_coupled_mutation_chain",
        "chain_schema": raw_spec.get("schema", CHAIN_SPEC_SCHEMA),
        "chain_json": str(args.chain_json),
        "fixture": "tests/fixtures/pinned_rollout_schedule.json",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "path_schema": payload["path_trace"]["schema"]}, indent=2))


if __name__ == "__main__":
    main()
