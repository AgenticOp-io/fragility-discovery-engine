#!/usr/bin/env python3
"""Print narrations for all checked-in coupled_institution fork artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.coupled_fork import COUPLED_FORK_ARTIFACT_NAMES, coupled_fork_artifacts_dir
from fragility_engine.explain.narration import load_frozen_json_artifact, narrate_frozen_artifact

# Optional fork artifacts narrated with the four golden-bundle files.
_EXTRA_NARRATION_NAMES: tuple[str, ...] = ("sample_coupled_pareto_front.json",)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--json-out-dir",
        type=Path,
        default=None,
        help="Write narration-summary-v1 JSON per artifact basename.",
    )
    ap.add_argument("--cite-digest", action="store_true", help="Prefix SHA-256 + path per artifact.")
    args = ap.parse_args()

    art = coupled_fork_artifacts_dir(ROOT)
    missing = [n for n in COUPLED_FORK_ARTIFACT_NAMES if not (art / n).is_file()]
    if missing:
        print(f"missing artifacts under {art}: {missing}", file=sys.stderr)
        print("Run: python scripts/regenerate_coupled_fork_artifacts.py", file=sys.stderr)
        raise SystemExit(1)

    if args.json_out_dir:
        args.json_out_dir.mkdir(parents=True, exist_ok=True)

    names = tuple(dict.fromkeys((*COUPLED_FORK_ARTIFACT_NAMES, *_EXTRA_NARRATION_NAMES)))
    for name in names:
        path = art / name
        resolved = path.resolve()
        cite = ""
        if args.cite_digest:
            digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
            cite = f"citation_sha256: {digest}\ncitation_path: {resolved.as_posix()}\n"
        data = load_frozen_json_artifact(path)
        text = narrate_frozen_artifact(data, source=str(resolved), citation_prefix=cite)
        print(f"=== {name} ===")
        print(text)
        print()
        if args.json_out_dir:
            summary: dict = {
                "schema": "narration-summary-v1",
                "input": str(resolved),
                "text": text,
            }
            if args.cite_digest:
                summary["input_sha256"] = hashlib.sha256(resolved.read_bytes()).hexdigest()
            out = args.json_out_dir / f"{path.stem}_narration.json"
            out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
