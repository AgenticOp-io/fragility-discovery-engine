#!/usr/bin/env python3
"""Write workbench status.json for GCE public site (server-side validation snapshot)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _git_head(repo: Path) -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                text=True,
            )
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts" / "public_site" / "status.json",
    )
    ap.add_argument("--release", default="v0.5.0")
    ap.add_argument(
        "--skip-validate",
        action="store_true",
        help="Only write git metadata (faster smoke).",
    )
    args = ap.parse_args()

    status: dict[str, object] = {
        "schema": "fragility-workbench-status-v1",
        "host": "gce",
        "release": args.release,
        "git_head": _git_head(ROOT),
        "checked_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "benchmark_validate": "skipped",
    }

    if not args.skip_validate:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_benchmark_suite.py"), "--validate"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        status["benchmark_validate"] = "ok" if proc.returncode == 0 else "failed"
        if proc.returncode != 0:
            status["validate_stderr"] = (proc.stderr or proc.stdout or "")[-2000:]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status, indent=2))
    if status.get("benchmark_validate") == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
