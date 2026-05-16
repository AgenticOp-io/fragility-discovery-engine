"""Validate attribution viewer preset manifest and bundled sample."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VIEWER_DIR = REPO_ROOT / "artifacts" / "attribution_viewer"
PRESETS_PATH = VIEWER_DIR / "local_presets.json"


def test_local_presets_schema_and_bundled_sample_exists() -> None:
    data = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    assert data.get("schema_version") == 1
    presets = data["presets"]
    assert isinstance(presets, list) and presets
    for entry in presets:
        assert entry.get("label") and entry.get("path")
        if entry["path"].startswith("sample_"):
            full = (VIEWER_DIR / entry["path"]).resolve()
            assert full.is_file(), f"missing bundled sample: {full}"


def test_bundled_attribution_merge_sample_schema() -> None:
    p = VIEWER_DIR / "sample_attribution_merge_resource_cascade.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("schema") == "attribution-merge-v1"
    assert isinstance(obj.get("nodes"), list) and obj["nodes"]
    assert isinstance(obj.get("edges"), list)
