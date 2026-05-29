"""Bundled coupled replay JSON must expose peg + overload series for the replay viewer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COUPLED_MODE = "coupled_institution_v1"
SAMPLES = (
    ROOT / "artifacts" / "replay_viewer" / "sample_coupled_institution_replay.json",
    ROOT / "forks" / "coupled_institution" / "artifacts" / "sample_coupled_replay.json",
)


@pytest.mark.parametrize("path", SAMPLES)
def test_coupled_replay_viewer_contract(path: Path) -> None:
    if not path.is_file():
        pytest.skip(f"missing {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("simulation_mode") == COUPLED_MODE
    assert data.get("schema_version")
    traj = data.get("trajectory") or []
    assert len(traj) >= 2
    for step in traj:
        metrics = step.get("metrics") or {}
        for key in ("price", "panic", "overload", "instability"):
            assert key in metrics, f"step {step.get('timestep')}: missing metrics.{key}"
            assert isinstance(metrics[key], (int, float))
        sv = step.get("state_vector") or []
        assert len(sv) >= 3, f"step {step.get('timestep')}: state_vector too short"
        assert metrics["panic"] == pytest.approx(float(sv[0]), rel=0, abs=1e-9)
        assert metrics["overload"] == pytest.approx(float(sv[1]), rel=0, abs=1e-9)
