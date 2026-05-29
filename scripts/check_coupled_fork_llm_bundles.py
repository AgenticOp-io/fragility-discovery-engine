#!/usr/bin/env python3
"""Fail if coupled fork LLM export bundles are missing or stale."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "artifacts" / "llm_prompts" / "coupled_fork_exports"
MANIFEST_SCHEMA = "coupled-fork-llm-exports-v1"

_EXPECTED_STEMS = (
    "sample_coupled_replay",
    "coupling_strength_sweep",
    "sample_coupling_comparison",
    "sample_coupled_mutation_chain",
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

    exports = manifest.get("exports") or []
    if len(exports) != len(_EXPECTED_STEMS):
        errors.append(f"manifest exports count {len(exports)} != {len(_EXPECTED_STEMS)}")

    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        raise SystemExit(1)

    print(f"OK: {len(_EXPECTED_STEMS)} coupled fork LLM bundles + manifest")


if __name__ == "__main__":
    main()
