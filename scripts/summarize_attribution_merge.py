"""Emit attribution-interaction-summary-v1 from an attribution-merge-v1 JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.explain.interaction_summary import summarize_attribution_merge


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Summarize merged counterfactual branches (additive delta sums; see interpretation_hint).",
    )
    ap.add_argument("--input", type=Path, required=True, help="attribution-merge-v1 JSON.")
    ap.add_argument("--out", type=Path, default=Path("attribution_interaction_summary.json"))
    args = ap.parse_args()

    try:
        merge = json.loads(args.input.read_text(encoding="utf-8"))
    except OSError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e
    except json.JSONDecodeError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e
    if not isinstance(merge, dict):
        raise SystemExit("--input must be a JSON object")

    try:
        summary = summarize_attribution_merge(merge)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e

    summary["meta"] = {"cli": "summarize_attribution_merge", "input": str(args.input)}
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
