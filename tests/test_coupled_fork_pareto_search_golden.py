"""Re-run coupled fork GA Pareto export and match pinned search metrics."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PIN_FILES = {
    "v1": ROOT / "tests" / "fixtures" / "benchmarks" / "coupled_fork_pareto_search_pins.json",
    "v2": ROOT / "tests" / "fixtures" / "benchmarks" / "coupled_fork_pareto_search_v2_pins.json",
}
EXPORT = ROOT / "scripts" / "export_coupled_fork_pareto.py"


@pytest.mark.skipif(
    not (ROOT / "forks" / "coupled_institution").is_dir(),
    reason="coupled_institution fork not present",
)
@pytest.mark.parametrize("tier", ["v1", "v2"])
def test_coupled_pareto_search_matches_pins(tmp_path: Path, tier: str) -> None:
    pins = json.loads(PIN_FILES[tier].read_text(encoding="utf-8"))
    search = pins["search"]
    out = tmp_path / "pareto.json"
    cmd = [
        sys.executable,
        str(EXPORT),
        "--out",
        str(out),
        "--seed",
        str(search["seed"]),
        "--generations",
        str(search["generations"]),
        "--population-size",
        str(search["population_size"]),
        "--horizon",
        str(search["horizon"]),
        "--coupling",
        str(search["coupling_strength"]),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    obj = json.loads(out.read_text(encoding="utf-8"))
    expected = pins["expected"]
    assert obj.get("schema") == "pareto-front-v1"
    assert float(obj["best_fitness"]) == pytest.approx(float(expected["best_fitness"]), rel=0, abs=1e-9)
    assert len(obj.get("archive") or []) == int(expected["archive_points"])


def test_bundled_coupled_pareto_passes_check_script() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_coupled_fork_pareto.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
