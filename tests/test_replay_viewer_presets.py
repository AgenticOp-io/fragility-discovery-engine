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
    for name in (
        "sample_replay.json",
        "sample_network_replay.json",
        "sample_resource_cascade_replay.json",
        "sample_service_backlog_replay.json",
        "sample_liquidity_ladder_replay.json",
    ):
        p = VIEWER_DIR / name
        obj = json.loads(p.read_text(encoding="utf-8"))
        assert isinstance(obj.get("trajectory"), list)
        assert obj.get("schema_version")


def test_sample_service_backlog_replay_matches_frozen_bundle() -> None:
    """Bundled JSON is the full replay for ``service_backlog_rollout_v1`` (pinned genome + seed)."""

    from fragility_engine.benchmarks.suite import GOLDEN_METRICS, run_bundle_rollout_once
    from fragility_engine.runner import rollout_to_replay_dict

    p = VIEWER_DIR / "sample_service_backlog_replay.json"
    on_disk = json.loads(p.read_text(encoding="utf-8"))
    r = run_bundle_rollout_once("service_backlog_rollout_v1")
    fresh = rollout_to_replay_dict(r)
    assert on_disk["simulation_mode"] == "service_backlog"
    assert on_disk["integral_instability"] == fresh["integral_instability"]
    assert on_disk["collapsed"] == fresh["collapsed"]
    gold = GOLDEN_METRICS["service_backlog_rollout_v1"]
    assert on_disk["integral_instability"] == gold["integral_instability"]
    assert on_disk["collapsed"] is gold["collapsed"]


def test_sample_liquidity_ladder_replay_matches_frozen_bundle() -> None:
    from fragility_engine.benchmarks.suite import GOLDEN_METRICS, run_bundle_rollout_once
    from fragility_engine.runner import rollout_to_replay_dict

    p = VIEWER_DIR / "sample_liquidity_ladder_replay.json"
    on_disk = json.loads(p.read_text(encoding="utf-8"))
    r = run_bundle_rollout_once("liquidity_ladder_rollout_v1")
    fresh = rollout_to_replay_dict(r)
    assert on_disk["simulation_mode"] == "liquidity_ladder"
    assert on_disk["integral_instability"] == fresh["integral_instability"]
    gold = GOLDEN_METRICS["liquidity_ladder_rollout_v1"]
    assert on_disk["integral_instability"] == gold["integral_instability"]
