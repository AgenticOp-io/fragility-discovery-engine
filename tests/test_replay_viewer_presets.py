"""Validate replay viewer preset manifest and bundled sample paths."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VIEWER_DIR = REPO_ROOT / "artifacts" / "replay_viewer"
PRESETS_PATH = VIEWER_DIR / "local_presets.json"


def _resolve_preset_path(rel: str) -> Path:
    return (VIEWER_DIR / rel).resolve()


def test_local_presets_schema_and_bundled_files_exist() -> None:
    data = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    assert data.get("schema_version") == 1
    presets = data["presets"]
    assert isinstance(presets, list) and presets
    for entry in presets:
        assert "label" in entry and "path" in entry
        assert isinstance(entry["label"], str) and entry["label"].strip()
        assert isinstance(entry["path"], str) and entry["path"].strip()
        full = _resolve_preset_path(entry["path"])
        if entry["path"].startswith("sample_"):
            assert full.is_file(), f"missing bundled sample: {full}"
        if "../test_exports/" in entry["path"]:
            # Optional local QA bundles (gitignored unless present).
            pass


def test_bundled_replay_samples_are_valid_json_with_trajectory() -> None:
    for name in ("sample_replay.json", "sample_network_replay.json"):
        p = VIEWER_DIR / name
        obj = json.loads(p.read_text(encoding="utf-8"))
        assert isinstance(obj.get("trajectory"), list)
        assert obj.get("schema_version")
