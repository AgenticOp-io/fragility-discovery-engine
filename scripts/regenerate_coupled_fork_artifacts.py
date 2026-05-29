#!/usr/bin/env python3
"""Regenerate coupled fork golden replay and copy into replay_viewer for site builds."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORK = ROOT / "forks" / "coupled_institution"
SAMPLE = FORK / "artifacts" / "sample_coupled_replay.json"
VIEWER_COPY = ROOT / "artifacts" / "replay_viewer" / "sample_coupled_institution_replay.json"
ATTR_COPY = ROOT / "artifacts" / "attribution_viewer" / "sample_coupled_mutation_chain.json"
DEMO_DIR = ROOT / "artifacts" / "coupled_fork_demo"
FORK_ART = FORK / "artifacts"
DEMO_NAMES = (
    "sample_coupled_replay.json",
    "coupling_strength_sweep.json",
    "sample_coupling_comparison.json",
    "sample_coupled_mutation_chain.json",
    "sample_coupled_pareto_front.json",
)
PARETO_VIEWER = ROOT / "artifacts" / "pareto_viewer" / "sample_pareto_coupled_institution.json"


def main() -> None:
    regen = FORK / "scripts" / "regenerate_golden.py"
    subprocess.run([sys.executable, str(regen)], cwd=FORK, check=True)
    subprocess.run(
        [sys.executable, str(FORK / "scripts" / "coupling_strength_sweep.py")],
        cwd=FORK,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(FORK / "scripts" / "export_coupling_comparison.py")],
        cwd=FORK,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(FORK / "scripts" / "export_coupled_mutation_chain.py")],
        cwd=FORK,
        check=True,
    )
    if not SAMPLE.is_file():
        raise SystemExit(f"Expected {SAMPLE} after regenerate")
    VIEWER_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SAMPLE, VIEWER_COPY)
    chain = FORK / "artifacts" / "sample_coupled_mutation_chain.json"
    if chain.is_file():
        ATTR_COPY.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(chain, ATTR_COPY)
    print(f"OK: {SAMPLE.relative_to(ROOT)}")
    print(f"OK: {VIEWER_COPY.relative_to(ROOT)}")
    if ATTR_COPY.is_file():
        print(f"OK: {ATTR_COPY.relative_to(ROOT)}")

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_coupled_fork_pareto.py"),
            "--also-fork-artifacts",
        ],
        cwd=str(ROOT),
        check=True,
    )
    if PARETO_VIEWER.is_file():
        print(f"OK: {PARETO_VIEWER.relative_to(ROOT)}")

    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    for name in DEMO_NAMES:
        src = FORK_ART / name
        if src.is_file():
            shutil.copy2(src, DEMO_DIR / name)
            print(f"OK: {(DEMO_DIR / name).relative_to(ROOT)}")

    sweep_json = FORK_ART / "coupling_strength_sweep.json"
    sweep_png = DEMO_DIR / "coupling_strength_sweep.png"
    if sweep_json.is_file():
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "plot_coupling_sweep.py"),
                str(sweep_json),
                "--out",
                str(sweep_png),
            ],
            cwd=str(ROOT),
            check=True,
        )
        print(f"OK: {sweep_png.relative_to(ROOT)}")

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "refresh_flagship_bundled_certificate.py")],
        cwd=str(ROOT),
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_coupled_fork_llm_prompts.py"),
            "--cite-digest",
        ],
        cwd=str(ROOT),
        check=True,
    )
    narr_out = ROOT / "artifacts" / "llm_prompts" / "coupled_fork_exports" / "narration_summaries"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "narrate_coupled_fork_bundle.py"),
            "--json-out-dir",
            str(narr_out),
            "--cite-digest",
        ],
        cwd=str(ROOT),
        check=True,
    )


if __name__ == "__main__":
    main()
