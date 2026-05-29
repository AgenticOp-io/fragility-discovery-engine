"""Reproducible ``fragility-certificate-v1`` — environment + benchmark fingerprints for citations."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from fragility_engine.benchmarks.manifest import build_benchmark_manifest

FRAGILITY_CERTIFICATE_SCHEMA = "fragility-certificate-v1"


def _try_git_head(repo_root: Path | None = None) -> str | None:
    try:
        cwd = str(repo_root) if repo_root is not None else None
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd,
            check=False,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _package_version() -> str:
    try:
        from importlib.metadata import version

        return version("fragility-engine")
    except Exception:
        return "unknown"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def digest_json_files(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for p in paths:
        rows.append({"path": str(p.resolve()), "sha256": sha256_file(p)})
    return rows


def build_fragility_certificate(
    *,
    artifact_paths: list[Path] | None = None,
    include_benchmark_manifest: bool = True,
    benchmark_validation: dict[str, Any] | None = None,
    research_fork_validation: dict[str, Any] | None = None,
    research_fork_artifact_paths: list[Path] | None = None,
    flagship_run: dict[str, Any] | None = None,
    git_commit: str | None = None,
    repo_root: Path | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """
    Assemble a machine-readable citation bundle (not a legal “certificate”).

    ``benchmark_validation`` should be small JSON-serializable metadata, e.g.
    ``{"status": "passed", "bundle_count": 5}`` or ``{"status": "failed", "error": "…"}``.
    """

    import numpy as np

    gc = git_commit or os.environ.get("FRAGILITY_GIT_COMMIT") or _try_git_head(repo_root)
    digests = digest_json_files(artifact_paths) if artifact_paths else []
    payload: dict[str, Any] = {
        "schema": FRAGILITY_CERTIFICATE_SCHEMA,
        "fragility_engine_version": _package_version(),
        "python_version": sys.version.split()[0],
        "numpy_version": str(np.__version__),
        "git_commit": gc,
        "artifact_sha256": digests,
    }
    if include_benchmark_manifest:
        bm = build_benchmark_manifest()
        payload["benchmark_manifest"] = bm
        payload["benchmark_golden_metrics_sha256"] = bm.get("golden_metrics_sha256")
        payload["benchmark_bundle_ids"] = list(bm.get("bundle_ids") or [])
    if benchmark_validation is not None:
        payload["benchmark_validation"] = benchmark_validation
    if research_fork_validation is not None:
        payload["research_fork_validation"] = research_fork_validation
    if research_fork_artifact_paths:
        payload["research_fork_artifact_sha256"] = digest_json_files(research_fork_artifact_paths)
    if flagship_run is not None:
        payload["flagship_run"] = flagship_run
    if notes.strip():
        payload["notes"] = notes.strip()
    payload["certificate_content_sha256"] = sha256_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return payload
