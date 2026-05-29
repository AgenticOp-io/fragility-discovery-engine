#!/usr/bin/env python3
"""Export reviewer_memo llm-prompt-bundle-v1 over the coupled fork export manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from export_llm_narration_prompt import build_prompt_bundle  # noqa: E402

MANIFEST = ROOT / "artifacts" / "llm_prompts" / "coupled_fork_exports" / "manifest.json"
DEFAULT_OUT = ROOT / "artifacts" / "llm_prompts" / "coupled_fork_exports" / "coupled_fork_reviewer_memo.llm_bundle.json"
REVIEWER_SCHEMA = "coupled-fork-reviewer-input-v1"


def _reviewer_input(manifest: dict[str, Any]) -> dict[str, Any]:
    exports = manifest.get("exports") or []
    lines = [
        f"manifest_schema: {manifest.get('schema')}",
        f"bundle_count: {manifest.get('bundle_count', len(exports))}",
        "",
        "exports:",
    ]
    for e in exports:
        if not isinstance(e, dict):
            continue
        lines.append(
            f"  - {e.get('artifact')}: pack={e.get('prompt_pack')} sha256={e.get('input_sha256', '?')[:16]}…"
        )
    return {
        "schema": REVIEWER_SCHEMA,
        "bundle_id": "coupled_institution_rollout_v1",
        "manifest_schema": manifest.get("schema"),
        "export_count": len(exports),
        "narration": "\n".join(lines),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--cite-digest", action="store_true")
    args = ap.parse_args()
    if not args.manifest.is_file():
        raise SystemExit(f"missing manifest: {args.manifest} (run export_coupled_fork_llm_prompts.py first)")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    summary_path = args.out.parent / "reviewer_input_summary.json"
    summary = _reviewer_input(manifest)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    bundle = build_prompt_bundle(
        summary_path,
        cite_digest=bool(args.cite_digest),
        prompt_pack="coupled_fork_reviewer_v1",
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(args.out), "prompt_pack": bundle.get("prompt_pack")}, indent=2))


if __name__ == "__main__":
    main()
