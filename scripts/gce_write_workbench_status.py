#!/usr/bin/env python3
"""Write workbench status.json for GCE public site (server-side validation snapshot)."""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STATUS_SCHEMA_V2 = "fragility-workbench-status-v2"
DEFAULT_PUBLIC_HOST = "hub.agenticop.io"  # DNS check only — same A record as this VM
DEFAULT_VM_IP = "34.61.255.147"


def _release_tag() -> str:
    try:
        import tomllib
    except ImportError:  # pragma: no cover
        import tomli as tomllib  # type: ignore

    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return f"v{data['project']['version']}"


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


def _run_check(script: str, *extra: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return "ok" if proc.returncode == 0 else "failed"


def _dns_ready(host: str, expected_ip: str) -> bool:
    try:
        return socket.gethostbyname(host) == expected_ip
    except OSError:
        return False


def _pypi_ready() -> str:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_pypi_ready.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return "ok"
    if "twine" in (proc.stderr or "").lower() or "build" in (proc.stderr or "").lower():
        return "failed"
    return "failed"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts" / "public_site" / "status.json",
    )
    ap.add_argument("--release", default=None, help="Defaults to v{pyproject version}")
    ap.add_argument(
        "--skip-validate",
        action="store_true",
        help="Only write git metadata (faster smoke).",
    )
    ap.add_argument("--public-host", default=DEFAULT_PUBLIC_HOST)
    ap.add_argument("--vm-ip", default=DEFAULT_VM_IP)
    args = ap.parse_args()

    release = args.release or _release_tag()
    status: dict[str, object] = {
        "schema": STATUS_SCHEMA_V2,
        "host": "gce",
        "release": release,
        "git_head": _git_head(ROOT),
        "checked_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "benchmark_validate": "skipped",
        "dns_ready": _dns_ready(args.public_host, args.vm_ip),
        "dns_host": args.public_host,
        "dns_expected_ip": args.vm_ip,
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

        fork_proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_coupled_fork_bundle.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        status["research_fork_validate"] = "ok" if fork_proc.returncode == 0 else "failed"
        status["research_fork_bundle_id"] = "coupled_institution_rollout_v1"
        if fork_proc.returncode != 0:
            status["research_fork_stderr"] = (fork_proc.stderr or fork_proc.stdout or "")[-2000:]

        status["coupled_fork_pareto_v1"] = _run_check("check_coupled_fork_pareto.py", "--tier", "v1")
        status["bundled_pareto_hypervolume"] = _run_check("check_bundled_pareto_hypervolume.py")
        status["pypi_ready"] = _pypi_ready()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status, indent=2))
    hard_fail = (
        status.get("benchmark_validate") == "failed"
        or status.get("research_fork_validate") == "failed"
        or status.get("coupled_fork_pareto_v1") == "failed"
        or status.get("bundled_pareto_hypervolume") == "failed"
    )
    if hard_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
