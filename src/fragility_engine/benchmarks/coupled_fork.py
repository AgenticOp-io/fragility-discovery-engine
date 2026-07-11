"""Research fork artifact paths and validation for ``coupled_institution``."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

COUPLED_FORK_BUNDLE_ID = "coupled_institution_rollout_v1"
COUPLED_FORK_TETRA_BUNDLE_ID = "coupled_institution_tetra_rollout_v1"
COUPLED_FORK_PARETO_SEARCH_BUNDLE_ID = "coupled_institution_pareto_search_v1"
COUPLED_FORK_PARETO_SEARCH_V2_BUNDLE_ID = "coupled_institution_pareto_search_v2"

COUPLED_FORK_ARTIFACT_NAMES: tuple[str, ...] = (
    "sample_coupled_replay.json",
    "coupling_strength_sweep.json",
    "sample_coupling_comparison.json",
    "sample_coupled_mutation_chain.json",
    "sample_coupled_tetra_replay.json",
    "sample_coupled_pareto_tetra.json",
    "worth_it_bar.json",
)


def coupled_fork_artifacts_dir(repo_root: Path | None = None) -> Path:
    root = repo_root if repo_root is not None else Path(__file__).resolve().parents[3]
    return root / "forks" / "coupled_institution" / "artifacts"


def coupled_fork_artifact_paths(repo_root: Path | None = None) -> list[Path]:
    art = coupled_fork_artifacts_dir(repo_root)
    return [art / name for name in COUPLED_FORK_ARTIFACT_NAMES if (art / name).is_file()]


def run_coupled_fork_bundle_validation(repo_root: Path | None = None) -> dict[str, Any]:
    """Run ``validate_coupled_fork_bundle.py``; return validation metadata for certificates."""

    root = repo_root if repo_root is not None else Path(__file__).resolve().parents[3]
    script = root / "scripts" / "validate_coupled_fork_bundle.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "validate_coupled_fork_bundle failed").strip()
        return {
            "status": "failed",
            "bundle_id": COUPLED_FORK_BUNDLE_ID,
            "tetra_bundle_id": COUPLED_FORK_TETRA_BUNDLE_ID,
            "error": err[:2000],
        }
    return {
        "status": "passed",
        "bundle_id": COUPLED_FORK_BUNDLE_ID,
        "tetra_bundle_id": COUPLED_FORK_TETRA_BUNDLE_ID,
    }
