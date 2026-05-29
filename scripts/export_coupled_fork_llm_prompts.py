#!/usr/bin/env python3
"""Export llm-prompt-bundle-v1 JSON for all checked-in coupled_institution fork artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from export_llm_narration_prompt import build_prompt_bundle  # noqa: E402
FORK_ART = ROOT / "forks" / "coupled_institution" / "artifacts"
DEFAULT_OUT = ROOT / "artifacts" / "llm_prompts" / "coupled_fork_exports"
MANIFEST_SCHEMA = "coupled-fork-llm-exports-v1"

# (artifact filename under fork artifacts/, prompt pack id, export basename)
_EXPORTS: tuple[tuple[str, str, str], ...] = (
    ("sample_coupled_replay.json", "coupled_institution_replay_v1", "sample_coupled_replay"),
    (
        "coupling_strength_sweep.json",
        "coupled_institution_coupling_sweep_v1",
        "coupling_strength_sweep",
    ),
    (
        "sample_coupling_comparison.json",
        "coupled_institution_comparison_v1",
        "sample_coupling_comparison",
    ),
    (
        "sample_coupled_mutation_chain.json",
        "coupled_institution_mutation_chain_v1",
        "sample_coupled_mutation_chain",
    ),
)


def export_all(*, out_dir: Path, cite_digest: bool) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for art_name, pack, stem in _EXPORTS:
        src = FORK_ART / art_name
        if not src.is_file():
            raise SystemExit(f"missing fork artifact: {src} (run regenerate_coupled_fork_artifacts.py)")
        bundle = build_prompt_bundle(src, cite_digest=cite_digest, prompt_pack=pack)
        out_path = out_dir / f"{stem}.llm_bundle.json"
        out_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
        try:
            bundle_rel = out_path.resolve().relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            bundle_rel = out_path.resolve().as_posix()
        entries.append(
            {
                "artifact": art_name,
                "prompt_pack": pack,
                "bundle_path": bundle_rel,
                "input_sha256": bundle.get("input_sha256"),
            }
        )
    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "bundle_count": len(entries),
        "exports": entries,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    try:
        out_rel = out_dir.resolve().relative_to(ROOT.resolve()).as_posix()
        manifest_rel = manifest_path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        out_rel = str(out_dir.resolve())
        manifest_rel = str(manifest_path.resolve())
    return {"out_dir": out_rel, "manifest": manifest_rel}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--cite-digest", action="store_true", help="Include SHA-256 of each source artifact.")
    args = ap.parse_args()
    summary = export_all(out_dir=args.out_dir, cite_digest=bool(args.cite_digest))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
