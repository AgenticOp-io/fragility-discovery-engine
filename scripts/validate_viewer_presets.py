"""Fail if static viewer preset manifests reference missing bundled JSON files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"

# Presets whose paths must exist when they start with these prefixes (checked-in bundles).
_REQUIRED_PREFIXES = ("sample_", "../composite_demo/sample_", "../flagship/bundled/")


def _check_viewer(viewer_dir: Path) -> list[str]:
    presets_path = viewer_dir / "local_presets.json"
    if not presets_path.is_file():
        return []
    errors: list[str] = []
    data = json.loads(presets_path.read_text(encoding="utf-8"))
    for entry in data.get("presets") or []:
        rel = str(entry.get("path") or "").strip()
        if not rel:
            errors.append(f"{viewer_dir.name}: empty preset path")
            continue
        if not rel.startswith(_REQUIRED_PREFIXES):
            continue
        target = (viewer_dir / rel).resolve()
        if not target.is_file():
            errors.append(f"{viewer_dir.name}: missing bundled preset file {rel} -> {target}")
    return errors


def main() -> None:
    errors: list[str] = []
    for sub in sorted(ARTIFACTS.iterdir()):
        if not sub.is_dir():
            continue
        if (sub / "local_presets.json").is_file():
            errors.extend(_check_viewer(sub))
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        raise SystemExit(1)
    print("OK: all bundled viewer preset paths exist")


if __name__ == "__main__":
    main()
