#!/usr/bin/env python3
"""Fail if coupled fork LLM export bundles are missing or stale."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.coupled_fork import COUPLED_FORK_ARTIFACT_NAMES, coupled_fork_artifacts_dir

ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "artifacts" / "llm_prompts" / "coupled_fork_exports"
FORK_ART = coupled_fork_artifacts_dir(ROOT)
MANIFEST_SCHEMA = "coupled-fork-llm-exports-v1"

_EXPECTED_STEMS = (
    "sample_coupled_replay",
    "coupling_strength_sweep",
    "sample_coupling_comparison",
    "sample_coupled_mutation_chain",
    "sample_coupled_pareto_front",
)


def main() -> None:
    manifest_path = EXPORT_DIR / "manifest.json"
    if not manifest_path.is_file():
        print(f"missing {manifest_path}", file=sys.stderr)
        print("Run: python scripts/export_coupled_fork_llm_prompts.py --cite-digest", file=sys.stderr)
        raise SystemExit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != MANIFEST_SCHEMA:
        print(f"unexpected manifest schema: {manifest.get('schema')}", file=sys.stderr)
        raise SystemExit(1)

    art_by_stem = {
        "sample_coupled_replay": "sample_coupled_replay.json",
        "coupling_strength_sweep": "coupling_strength_sweep.json",
        "sample_coupling_comparison": "sample_coupling_comparison.json",
        "sample_coupled_mutation_chain": "sample_coupled_mutation_chain.json",
        "sample_coupled_pareto_front": "sample_coupled_pareto_front.json",
    }

    errors: list[str] = []
    for stem in _EXPECTED_STEMS:
        p = EXPORT_DIR / f"{stem}.llm_bundle.json"
        if not p.is_file():
            errors.append(f"missing bundle: {p.relative_to(ROOT)}")
            continue
        bundle = json.loads(p.read_text(encoding="utf-8"))
        if bundle.get("schema") != "llm-prompt-bundle-v1":
            errors.append(f"{p.name}: not llm-prompt-bundle-v1")
        if not bundle.get("user_prompt"):
            errors.append(f"{p.name}: empty user_prompt")
        art_name = art_by_stem[stem]
        src = FORK_ART / art_name
        if src.is_file() and bundle.get("input_sha256"):
            live = hashlib.sha256(src.read_bytes()).hexdigest()
            if live != bundle["input_sha256"]:
                errors.append(f"{p.name}: input_sha256 stale (re-run export_coupled_fork_llm_prompts.py)")

    exports = manifest.get("exports") or []
    if len(exports) != len(_EXPECTED_STEMS):
        errors.append(f"manifest exports count {len(exports)} != {len(_EXPECTED_STEMS)}")

    narr_dir = EXPORT_DIR / "narration_summaries"
    narr_names = tuple(dict.fromkeys((*COUPLED_FORK_ARTIFACT_NAMES, "sample_coupled_pareto_front.json")))
    for name in narr_names:
        narr = narr_dir / f"{Path(name).stem}_narration.json"
        if not narr.is_file():
            errors.append(f"missing narration summary: {narr.relative_to(ROOT)}")

    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        raise SystemExit(1)

    print(f"OK: {len(_EXPECTED_STEMS)} coupled fork LLM bundles + manifest")


if __name__ == "__main__":
    main()
