"""Validate composite viewer preset manifest and bundled sample target."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSITE_VIEWER = REPO_ROOT / "artifacts" / "composite_viewer"
PRESETS_PATH = COMPOSITE_VIEWER / "local_presets.json"


def test_composite_viewer_presets_and_quad_sample() -> None:
    data = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    assert data.get("schema_version") == 1
    presets = data["presets"]
    assert len(presets) >= 1
    quad = (COMPOSITE_VIEWER / presets[0]["path"]).resolve()
    assert quad.is_file()
    obj = json.loads(quad.read_text(encoding="utf-8"))
    assert str(obj.get("schema", "")).startswith("fragility-institutional-composite-v")
    assert "network" in obj and "resource_cascade" in obj
