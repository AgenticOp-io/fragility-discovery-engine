"""Light subprocess smoke for CLI scripts (repo root as cwd)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def py_exe() -> str:
    return sys.executable


def test_week1_smoke_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "w.json"
    subprocess.run(
        [py_exe, str(ROOT / "scripts" / "week1_smoke.py"), "--export-replay", str(out)],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"]
    assert data["meta"]["cli"] == "week1_smoke"
    assert data["trajectory"]


def test_fragility_surface_cli_minimal_grid(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "g.csv"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_surface.py"),
            "--out",
            str(out),
            "--panic-points",
            "3",
            "--depeg-points",
            "3",
            "--steps",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
    )
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 10
    assert "integral_instability" in lines[0]


def test_export_counterfactual_writes_replay_pair(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "cf.json"
    repdir = tmp_path / "replays"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--out",
            str(out_json),
            "--export-replay-dir",
            str(repdir),
            "--horizon",
            "10",
            "--remove",
            "0",
            "--seed",
            "11",
            "--genome-seed",
            "12",
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert out_json.is_file()
    b = json.loads((repdir / "baseline.json").read_text(encoding="utf-8"))
    c = json.loads((repdir / "counterfactual.json").read_text(encoding="utf-8"))
    assert b["meta"]["variant"] == "baseline"
    assert c["meta"]["variant"] == "counterfactual"


def test_export_replay_network_watts_strogatz(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "ws.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "network",
            "--out",
            str(out),
            "--nodes",
            "14",
            "--graph-kind",
            "watts_strogatz",
            "--ws-k",
            "4",
            "--ws-p",
            "0.15",
            "--horizon",
            "12",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["topology"]["kind"] == "watts_strogatz"
    assert data["meta"]["topology"]["k"] == 4
    assert "undirected_edges" in data["meta"]["topology"]
    assert data["meta"]["topology"]["undirected_edges"] >= 1


def test_export_replay_network_continue_after_collapse_runs(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "nw.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "network",
            "--out",
            str(out),
            "--nodes",
            "12",
            "--horizon",
            "10",
            "--continue-after-collapse",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "network"
    assert data["meta"].get("continue_after_collapse") is True


def test_export_replay_aggregate_continue_after_collapse_runs(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cont.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--out",
            str(out),
            "--horizon",
            "14",
            "--continue-after-collapse",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"].get("continue_after_collapse") is True
    assert "recovery_timestep" in data


def test_run_mc_demo_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "mc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_mc_demo.py"),
            "--samples",
            "12",
            "--horizon",
            "12",
            "--seed",
            "404",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["cli"] == "run_mc_demo"


def test_compare_replays_cli(py_exe: str, tmp_path: Path) -> None:
    left = tmp_path / "a.json"
    right = tmp_path / "b.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--out",
            str(left),
            "--horizon",
            "14",
            "--seed",
            "7",
            "--genome-seed",
            "8",
            "--initial-panic",
            "0.06",
        ],
        check=True,
        cwd=str(ROOT),
    )
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--out",
            str(right),
            "--horizon",
            "14",
            "--seed",
            "7",
            "--genome-seed",
            "8",
            "--initial-panic",
            "0.42",
        ],
        check=True,
        cwd=str(ROOT),
    )
    diff_path = tmp_path / "cmp.json"
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "compare_replays.py"),
            str(left),
            str(right),
            "--out",
            str(diff_path),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    out = json.loads(proc.stdout)
    assert len(out["diff_keys"]) >= 1
    assert diff_path.is_file()
    assert json.loads(diff_path.read_text(encoding="utf-8"))["diff_keys"] == out["diff_keys"]


def test_export_minimized_replay_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "min.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_minimized_replay.py"),
            "--out",
            str(out),
            "--horizon",
            "26",
            "--max-tries",
            "180",
            "--genome-search-seed",
            "99",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["cli"] == "export_minimized_replay"
    assert data["trajectory"]


def test_run_ga_demo_exports_replay_variants(py_exe: str, tmp_path: Path) -> None:
    best = tmp_path / "best.json"
    mini = tmp_path / "mini.json"
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_ga_demo.py"),
            "--generations",
            "3",
            "--population-size",
            "12",
            "--seed",
            "999",
            "--export-replay",
            str(best),
            "--export-minimized-replay",
            str(mini),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(best.read_text(encoding="utf-8"))
    assert data["meta"]["variant"] == "best_ga"
    assert data["meta"]["ga_seed"] == 999
    if mini.is_file():
        m = json.loads(mini.read_text(encoding="utf-8"))
        assert m["meta"]["variant"] == "greedy_minimized_schedule"
    else:
        assert "Skipping --export-minimized-replay" in proc.stderr


def test_run_coevolution_aggregate_continue_after_collapse(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "coev_cont.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "aggregate",
            "--rounds",
            "1",
            "--max-steps",
            "36",
            "--attacker-horizon",
            "12",
            "--attacker-generations",
            "2",
            "--attacker-population",
            "8",
            "--defender-generations",
            "2",
            "--defender-population",
            "7",
            "--seed",
            "515151",
            "--continue-after-collapse",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "aggregate"
    assert data["meta"]["continue_after_collapse"] is True
    assert "recovery_timestep" in data


def test_benchmark_rollout_cli_smoke(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--mode",
            "aggregate",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--max-steps",
            "12",
            "--horizon",
            "10",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["mode"] == "aggregate"
    assert data["repeat"] == 1
    proc2 = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--mode",
            "network",
            "--nodes",
            "16",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--max-steps",
            "10",
            "--horizon",
            "8",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    net = json.loads(proc2.stdout)
    assert net["mode"] == "network"
    assert net["nodes"] == 16


def test_export_replay_network_neighbor_json_smoke(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "neighbors.json"
    nb.write_text("[[1],[0]]", encoding="utf-8")
    out = tmp_path / "ring.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "network",
            "--out",
            str(out),
            "--neighbor-json",
            str(nb),
            "--horizon",
            "10",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    topo = data["meta"]["topology"]
    assert topo["storage"] == "neighbor_lists"
    assert topo["n_nodes"] == 2
    assert topo["directed"] is True


def test_run_coevolution_neighbor_json_exports_replay(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "nl.json"
    nb.write_text("[[1,2],[0,2],[0,1]]", encoding="utf-8")
    out = tmp_path / "coev_nl.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "network",
            "--neighbor-json",
            str(nb),
            "--rounds",
            "1",
            "--max-steps",
            "28",
            "--attacker-horizon",
            "8",
            "--attacker-generations",
            "2",
            "--attacker-population",
            "8",
            "--defender-generations",
            "2",
            "--defender-population",
            "6",
            "--seed",
            "777001",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "network"
    assert data["meta"]["topology"]["storage"] == "neighbor_lists"
    assert data["meta"]["topology"]["n_nodes"] == 3


def test_run_coevolution_collect_attacker_pareto_in_summary(py_exe: str, tmp_path: Path) -> None:
    summary_path = tmp_path / "sum.json"
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "aggregate",
            "--rounds",
            "1",
            "--max-steps",
            "30",
            "--attacker-horizon",
            "8",
            "--attacker-generations",
            "2",
            "--attacker-population",
            "10",
            "--defender-generations",
            "2",
            "--defender-population",
            "7",
            "--seed",
            "600613",
            "--collect-attacker-pareto",
            "--json-summary",
            str(summary_path),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    stdout_payload = json.loads(proc.stdout)
    file_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert stdout_payload == file_payload
    rd0 = file_payload["rounds"][0]
    assert "attacker_pareto" in rd0
    assert len(rd0["attacker_pareto"]) >= 1


def test_run_coevolution_network_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "coev_net.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "network",
            "--nodes",
            "14",
            "--rounds",
            "1",
            "--attacker-horizon",
            "10",
            "--attacker-generations",
            "2",
            "--attacker-population",
            "8",
            "--defender-generations",
            "2",
            "--defender-population",
            "7",
            "--seed",
            "424242",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "network"
    assert data["meta"]["cli"] == "run_coevolution"
    assert data["meta"]["coevolution_mode"] == "network"
    assert data["meta"]["topology"]["kind"] == "erdos_renyi"
    assert "undirected_edges" in data["meta"]["topology"]


def test_run_coevolution_export_pareto_json(py_exe: str, tmp_path: Path) -> None:
    pf = tmp_path / "front.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "aggregate",
            "--rounds",
            "1",
            "--max-steps",
            "28",
            "--attacker-horizon",
            "8",
            "--attacker-generations",
            "2",
            "--attacker-population",
            "10",
            "--defender-generations",
            "2",
            "--defender-population",
            "6",
            "--seed",
            "910911",
            "--export-pareto-json",
            str(pf),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(pf.read_text(encoding="utf-8"))
    assert data["schema"] == "pareto-front-v1"
    assert len(data["archive"]) >= 1
    assert data["source"] == "run_coevolution"


def test_export_coevolution_pareto_script(py_exe: str, tmp_path: Path) -> None:
    summary_path = tmp_path / "sum.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "aggregate",
            "--rounds",
            "1",
            "--max-steps",
            "26",
            "--attacker-horizon",
            "7",
            "--attacker-generations",
            "2",
            "--attacker-population",
            "9",
            "--defender-generations",
            "2",
            "--defender-population",
            "6",
            "--seed",
            "606606",
            "--collect-attacker-pareto",
            "--json-summary",
            str(summary_path),
        ],
        check=True,
        cwd=str(ROOT),
    )
    out = tmp_path / "from_script.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_coevolution_pareto.py"),
            "--from-summary",
            str(summary_path),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "pareto-front-v1"
    assert data["source"] == "export_coevolution_pareto"


def test_export_counterfactual_network_writes_replays(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "cf_net.json"
    repdir = tmp_path / "replays_net"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "network",
            "--out",
            str(out_json),
            "--export-replay-dir",
            str(repdir),
            "--nodes",
            "14",
            "--horizon",
            "12",
            "--remove",
            "0",
            "--seed",
            "31",
            "--genome-seed",
            "32",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["meta"]["mode"] == "network"
    assert payload["baseline"]["mode"] == "network"
    assert "topology" in payload["meta"]
    b = json.loads((repdir / "baseline.json").read_text(encoding="utf-8"))
    assert b["meta"]["variant"] == "baseline"
    assert b["simulation_mode"] == "network"
