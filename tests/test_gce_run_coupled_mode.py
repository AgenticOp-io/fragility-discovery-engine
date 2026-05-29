"""GCE runner whitelist includes coupled_institution research fork."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "scripts" / "gce_run_server.py"


def _load_server():
    spec = importlib.util.spec_from_file_location("gce_run_server_coupled_test", SERVER_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gce_run_server_coupled_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_coupled_institution_in_modes_and_build_cmd() -> None:
    srv = _load_server()
    assert "coupled_institution" in srv.MODES
    assert "coupled_institution" in srv.HORIZON_AWARE_MODES
    req = {
        "mode": "coupled_institution",
        "seed": 42,
        "horizon": 12,
        "generations": 3,
        "population": 10,
        "initial_level": 0.25,
    }
    run_dir = ROOT / "artifacts" / "test_exports" / "_gce_cmd_probe"
    run_dir.mkdir(parents=True, exist_ok=True)
    cmd = srv._build_cmd(req, run_dir)
    joined = " ".join(cmd)
    assert "run_coupled_fork_demo.py" in joined
    assert "--export-replay" in cmd
    assert "--export-pareto" in cmd
    assert "--coupling" in cmd
    assert "0.25" in joined
