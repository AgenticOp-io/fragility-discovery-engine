"""Run frozen Phase H benchmark bundles (deterministic regression harness)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.benchmarks import BUNDLE_IDS, run_benchmark_suite, validate_benchmark_suite
from fragility_engine.benchmarks.suite import run_phase_h_search_microbench


def main() -> None:
    ap = argparse.ArgumentParser(description="Execute benchmark-bundle suite (see benchmarks/README.md).")
    ap.add_argument(
        "--validate",
        action="store_true",
        help="Exit non-zero if any bundle deviates from golden metrics.",
    )
    ap.add_argument("--json", action="store_true", help="Print results as JSON array.")
    ap.add_argument(
        "--manifest-out",
        type=Path,
        default=None,
        help="Write benchmark-manifest-v2 JSON (bundles + provenance + golden digest + tooling refs).",
    )
    ap.add_argument(
        "--bench-search",
        choices=("mc", "ga"),
        default=None,
        help="Run one Phase H search microbench (same semantics as benchmark_rollout --bench-search).",
    )
    ap.add_argument(
        "--eval-workers",
        type=int,
        default=1,
        help="With --bench-search: pool size for fitness evaluation.",
    )
    ap.add_argument(
        "--eval-pool",
        choices=("threads", "processes"),
        default="threads",
        help="With --bench-search: threads (default) or processes.",
    )
    ap.add_argument("--search-generations", type=int, default=2, help="With --bench-search ga: generations.")
    ap.add_argument("--search-population", type=int, default=8, help="With --bench-search ga: population size.")
    ap.add_argument("--search-samples", type=int, default=16, help="With --bench-search mc: samples.")
    ap.add_argument(
        "--search-seed",
        type=int,
        default=None,
        help="With --bench-search: search RNG seed (default pinned genome seed).",
    )
    args = ap.parse_args()

    if args.manifest_out is not None:
        from fragility_engine.benchmarks.manifest import build_benchmark_manifest

        args.manifest_out.write_text(json.dumps(build_benchmark_manifest(), indent=2), encoding="utf-8")

    if args.validate:
        try:
            validate_benchmark_suite()
        except AssertionError as e:
            print(str(e), file=sys.stderr)
            raise SystemExit(1) from e
        if not args.json and args.bench_search is None:
            print(f"OK: {len(BUNDLE_IDS)} bundles match golden metrics.")

    if args.bench_search is not None:
        payload = run_phase_h_search_microbench(
            bench_search=str(args.bench_search),
            eval_workers=int(args.eval_workers),
            eval_pool=str(args.eval_pool),
            search_seed=args.search_seed,
            generations=int(args.search_generations),
            population_size=int(args.search_population),
            samples=int(args.search_samples),
        )
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(
                f"search_microbench {payload['bench_search']}  eval_workers={payload['eval_workers']}  "
                f"eval_pool={payload['eval_pool']}  total_wall={payload['total_wall_clock_s']:.4f}s"
            )
            for row in payload["bundles"]:
                print(f"  {row['bundle_id']}: {row['mean_ms_per_search']:.3f} ms")
        return

    if args.validate:
        return

    results = run_benchmark_suite()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for row in results:
            print(
                f"{row['bundle_id']}: integral={row['integral_instability']:.6f} "
                f"collapsed={row['collapsed']} mode={row['simulation_mode']}"
            )


if __name__ == "__main__":
    main()
