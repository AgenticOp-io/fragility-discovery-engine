"""Generate a reviewer-oriented artifact bundle (GA replay + Pareto + fragility-certificate-v1)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fragility_engine.benchmarks.flagship import run_flagship_demo


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Write best_replay.json, pareto_front.json, fragility_certificate.json, README_FLAGSHIP.txt "
            "under the output directory (default: artifacts/flagship/output)."
        )
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts/flagship/output"),
        help="Directory to create / write into.",
    )
    p.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip Phase H validate_benchmark_suite before the GA (faster local smoke).",
    )
    p.add_argument("--horizon", type=int, default=14)
    p.add_argument("--generations", type=int, default=3)
    p.add_argument("--population-size", type=int, default=12)
    p.add_argument("--ga-seed", type=int, default=424_242)
    p.add_argument("--max-steps", type=int, default=36)
    p.add_argument("--eval-workers", type=int, default=1)
    p.add_argument("--json-summary", type=Path, default=None, help="Optional path for machine-readable run summary.")
    args = p.parse_args()

    result = run_flagship_demo(
        Path(args.out_dir),
        validate_bundles_first=not bool(args.skip_validate),
        horizon=int(args.horizon),
        generations=int(args.generations),
        population_size=int(args.population_size),
        ga_seed=int(args.ga_seed),
        max_steps=int(args.max_steps),
        eval_workers=max(1, int(args.eval_workers)),
    )

    print(json.dumps({"output_dir": result["output_dir"], "files": result["files"]}, indent=2))
    if args.json_summary is not None:
        args.json_summary.write_text(
            json.dumps(
                {
                    "cli": "run_flagship_demo",
                    "certificate_content_sha256": result["certificate"].get("certificate_content_sha256"),
                    "git_commit": result["certificate"].get("git_commit"),
                },
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
