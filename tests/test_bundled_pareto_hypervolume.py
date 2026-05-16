"""Regression: hypervolume pins on bundled pareto_viewer samples."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min, nondominated_points_min

ROOT = Path(__file__).resolve().parents[1]
PARETO_VIEWER = ROOT / "artifacts" / "pareto_viewer"
FIXTURE = ROOT / "tests" / "fixtures" / "benchmarks" / "bundled_pareto_hypervolume_pins.json"


@pytest.mark.parametrize(
    "filename",
    [
        "sample_pareto_front.json",
        "sample_pareto_resource_cascade.json",
        "sample_pareto_service_backlog.json",
        "sample_pareto_network.json",
        "sample_pareto_liquidity_ladder.json",
    ],
)
def test_bundled_pareto_hypervolume_pin(filename: str) -> None:
    pins = json.loads(FIXTURE.read_text(encoding="utf-8"))
    pin = pins[filename]
    obj = json.loads((PARETO_VIEWER / filename).read_text(encoding="utf-8"))
    pts = [(float(e["severity"]), float(e["attack_cost"])) for e in obj["archive"]]
    nd = nondominated_points_min(pts)
    ref = tuple(pin["hypervolume_reference"])
    hv = hypervolume_2d_min(nd, ref)
    assert hv == pytest.approx(float(pin["expected_hypervolume"]))


def test_check_bundled_pareto_hypervolume_script() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_bundled_pareto_hypervolume.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
