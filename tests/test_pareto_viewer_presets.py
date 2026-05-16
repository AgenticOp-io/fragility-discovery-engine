"""Validate Pareto viewer preset manifest and bundled sample."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PARETO_VIEWER = REPO_ROOT / "artifacts" / "pareto_viewer"
PRESETS_PATH = PARETO_VIEWER / "local_presets.json"


def test_local_presets_schema_and_bundled_sample() -> None:
    data = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    assert data.get("schema_version") == 1
    presets = data["presets"]
    assert isinstance(presets, list) and len(presets) >= 1
    for entry in presets:
        assert entry.get("label") and entry.get("path")
        full = (PARETO_VIEWER / entry["path"]).resolve()
        if "sample_pareto" in entry["path"]:
            assert full.is_file(), f"missing bundled sample: {full}"


def test_bundled_pareto_sample_has_archive() -> None:
    p = PARETO_VIEWER / "sample_pareto_front.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("schema") == "pareto-front-v1"
    arch = obj.get("archive")
    assert isinstance(arch, list) and len(arch) >= 1
    row = arch[0]
    assert "severity" in row and "attack_cost" in row
    assert "integral_instability" in row


def test_bundled_pareto_service_backlog_sample_has_archive() -> None:
    p = PARETO_VIEWER / "sample_pareto_service_backlog.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("schema") == "pareto-front-v1"
    arch = obj.get("archive")
    assert isinstance(arch, list) and len(arch) >= 1
    row = arch[0]
    assert "severity" in row and "attack_cost" in row
    assert "integral_instability" in row
