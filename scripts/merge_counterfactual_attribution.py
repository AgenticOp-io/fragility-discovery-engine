"""Merge counterfactual JSON exports that share the same baseline into one attribution graph."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.explain.merge_attribution import merge_heterogeneous_counterfactuals


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Load two or more export_counterfactual JSON payloads and emit attribution-merge-v1 "
            "(star graph: one baseline root, heterogeneous intervention branches)."
        ),
    )
    ap.add_argument(
        "--inputs",
        type=Path,
        nargs="+",
        required=True,
        help="Paths to counterfactual JSON files (same genome + rollout seed recommended).",
    )
    ap.add_argument("--out", type=Path, default=Path("attribution_merge.json"))
    ap.add_argument(
        "--no-strict-baseline",
        action="store_true",
        help="Do not require matching baseline snapshots across inputs.",
    )
    args = ap.parse_args()

    bundles: list[dict] = []
    for p in args.inputs:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except OSError as e:
            print(str(e), file=sys.stderr)
            raise SystemExit(2) from e
        except json.JSONDecodeError as e:
            print(f"{p}: {e}", file=sys.stderr)
            raise SystemExit(2) from e
        if not isinstance(data, dict):
            print(f"{p}: expected JSON object", file=sys.stderr)
            raise SystemExit(2)
        bundles.append(data)

    merged = merge_heterogeneous_counterfactuals(bundles, strict_baseline=not args.no_strict_baseline)
    merged["meta"] = {"cli": "merge_counterfactual_attribution", "inputs": [str(p) for p in args.inputs]}
    args.out.write_text(json.dumps(merged, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
