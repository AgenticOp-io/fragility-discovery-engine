"""Emit explanation-dag-v1 from a minimization report JSON or a counterfactual bundle JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from fragility_engine.explain.explanation_dag import (
    EXPLANATION_DAG_SCHEMA,
    counterfactual_bundle_to_dag,
    minimization_report_to_dag,
    mutation_chain_path_to_dag,
)


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise SystemExit(str(e)) from e
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path}: {e}") from e
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return data


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True, help="Write explanation-dag-v1 JSON here.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--from-minimization-report",
        type=Path,
        metavar="PATH",
        help="JSON from minimize_schedule / minimize_schedule_with_rollout report dict.",
    )
    src.add_argument(
        "--from-counterfactual",
        type=Path,
        metavar="PATH",
        help="Counterfactual export JSON with baseline + counterfactual + intervention.",
    )
    src.add_argument(
        "--from-mutation-chain",
        type=Path,
        metavar="PATH",
        help="Coupled fork mutation-chain export JSON with path_trace.nodes/edges.",
    )
    args = ap.parse_args()

    if args.from_minimization_report is not None:
        raw = _load(args.from_minimization_report)
        dag = minimization_report_to_dag(raw, source=str(args.from_minimization_report.resolve()))
    elif args.from_counterfactual is not None:
        raw = _load(args.from_counterfactual)
        dag = counterfactual_bundle_to_dag(raw, source=str(args.from_counterfactual.resolve()))
    else:
        raw = _load(args.from_mutation_chain)
        dag = mutation_chain_path_to_dag(raw, source=str(args.from_mutation_chain.resolve()))

    if dag.get("schema") != EXPLANATION_DAG_SCHEMA:
        print("internal error: wrong schema", file=sys.stderr)
        raise SystemExit(3)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(dag, indent=2), encoding="utf-8")
    print(json.dumps({"wrote": str(args.out), "schema": EXPLANATION_DAG_SCHEMA, "kind": dag.get("kind")}, indent=2))


if __name__ == "__main__":
    main()
