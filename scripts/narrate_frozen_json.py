"""Phase L wrapper: human-readable narration over frozen engine JSON.

Supports replay rollouts, Pareto archives, attribution merge, epsilon sweeps,
counterfactual bundles, **institutional composite** (v1/v2), and a few other
schemas implemented in ``fragility_engine.explain.narration``. Output is **not**
fed back into simulation — summaries cite artifact keys only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from fragility_engine.explain.narration import load_frozen_json_artifact, narrate_frozen_artifact


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Print short narration for frozen engine JSON (replay, Pareto, merge, composite, …)."
    )
    ap.add_argument("json_path", type=Path, help="Path to .json artifact.")
    ap.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path for narration-summary-v1 JSON (machine-readable).",
    )
    ap.add_argument(
        "--cite-digest",
        action="store_true",
        help="Prefix SHA-256 (raw file bytes) + resolved path for reproducible citations (Phase L hook).",
    )
    args = ap.parse_args()

    resolved = args.json_path.resolve()
    cite_prefix = ""
    digest_hex: str | None = None
    if args.cite_digest:
        raw = resolved.read_bytes()
        digest_hex = hashlib.sha256(raw).hexdigest()
        cite_prefix = f"citation_sha256: {digest_hex}\ncitation_path: {resolved.as_posix()}"

    try:
        data = load_frozen_json_artifact(args.json_path)
    except ValueError as e:
        raise SystemExit(str(e)) from e
    text = narrate_frozen_artifact(data, source=str(resolved), citation_prefix=cite_prefix)
    print(text)

    if args.json_out is not None:
        summary: dict[str, Any] = {
            "schema": "narration-summary-v1",
            "input": str(resolved),
            "text": text,
        }
        if digest_hex is not None:
            summary["input_sha256"] = digest_hex
        args.json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
