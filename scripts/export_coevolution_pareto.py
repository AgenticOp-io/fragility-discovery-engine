"""Convert ``run_coevolution`` JSON summary into ``pareto-front-v1`` for the static Pareto viewer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fragility_engine.coevolution.pareto_export import (
    flatten_coevolution_attacker_pareto,
    pareto_front_payload_from_archive_dicts,
)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Read co-evolution summary JSON (with rounds[].attacker_pareto) -> pareto_front JSON.",
    )
    ap.add_argument(
        "--from-summary",
        type=Path,
        required=True,
        help="JSON file like run_coevolution --json-summary output.",
    )
    ap.add_argument("--out", type=Path, default=Path("pareto_front.json"))
    args = ap.parse_args()

    try:
        data = json.loads(args.from_summary.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(str(e)) from e

    rounds = data.get("rounds")
    if not isinstance(rounds, list):
        raise SystemExit("Summary JSON must contain a 'rounds' array.")

    entries = flatten_coevolution_attacker_pareto(rounds)
    if not entries:
        raise SystemExit(
            "No attacker_pareto points found. Re-run co-evolution with --collect-attacker-pareto "
            "(or --export-pareto-json on run_coevolution, which enables collection automatically).",
        )

    payload = pareto_front_payload_from_archive_dicts(
        entries,
        source="export_coevolution_pareto",
    )
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
