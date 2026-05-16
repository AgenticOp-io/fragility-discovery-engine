"""Validate composite viewer preset manifest and bundled sample targets."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSITE_VIEWER = REPO_ROOT / "artifacts" / "composite_viewer"
PRESETS_PATH = COMPOSITE_VIEWER / "local_presets.json"
COMPOSITE_DEMO = REPO_ROOT / "artifacts" / "composite_demo"


def test_composite_viewer_presets_and_bundled_samples() -> None:
    data = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    assert data.get("schema_version") == 1
    presets = data["presets"]
    assert len(presets) >= 2
    for entry in presets:
        full = (COMPOSITE_VIEWER / entry["path"]).resolve()
        assert full.is_file(), f"missing {full}"
    triple = json.loads((COMPOSITE_DEMO / "sample_triple_composite.json").read_text(encoding="utf-8"))
    assert triple["schema"] == "fragility-institutional-composite-v2"
    assert "aggregate" in triple
    quad = json.loads((COMPOSITE_DEMO / "sample_quad_composite.json").read_text(encoding="utf-8"))
    assert quad["schema"] == "fragility-institutional-composite-v3"
    assert "service_backlog" in quad
