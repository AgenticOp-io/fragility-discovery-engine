from __future__ import annotations

import json
from pathlib import Path

from fragility_engine.benchmarks.flagship import run_flagship_demo


def test_run_flagship_demo_writes_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "flag"
    result = run_flagship_demo(out, validate_bundles_first=False, generations=2, population_size=8, horizon=10)
    assert (out / "best_replay.json").is_file()
    assert (out / "pareto_front.json").is_file()
    assert (out / "fragility_certificate.json").is_file()
    assert (out / "README_FLAGSHIP.txt").is_file()
    cert = json.loads((out / "fragility_certificate.json").read_text(encoding="utf-8"))
    assert cert["schema"] == "fragility-certificate-v1"
    assert result["certificate"]["schema"] == "fragility-certificate-v1"
