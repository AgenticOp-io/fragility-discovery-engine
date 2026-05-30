"""Fail if any checked-in bundled demo JSON listed in bundled_artifacts.py is missing or malformed."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.bundled_artifacts import BUNDLED_ARTIFACT_PATHS

ROOT = Path(__file__).resolve().parents[1]


def _validate_json_artifact(path: Path) -> str | None:
    """Return error message if JSON artifact lacks schema identity, else None."""

    if path.suffix.lower() != ".json":
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return f"{path}: invalid JSON ({exc})"
    if not isinstance(obj, dict):
        return f"{path}: expected top-level object"
    if "schema" in obj or "schema_version" in obj:
        return None
    return f"{path}: missing 'schema' or 'schema_version'"


def main() -> None:
    missing: list[str] = []
    invalid: list[str] = []
    for rel in BUNDLED_ARTIFACT_PATHS:
        p = ROOT / rel
        if not p.is_file():
            missing.append(rel)
            continue
        err = _validate_json_artifact(p)
        if err:
            invalid.append(err)
    if missing:
        for rel in missing:
            print(f"missing bundled artifact: {rel}", file=sys.stderr)
        print("Run: python scripts/regenerate_bundled_viewer_samples.py", file=sys.stderr)
        raise SystemExit(1)
    if invalid:
        for msg in invalid:
            print(msg, file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: {len(BUNDLED_ARTIFACT_PATHS)} bundled artifact paths exist and JSON samples declare schema")


if __name__ == "__main__":
    main()
