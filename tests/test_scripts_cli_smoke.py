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


def test_export_counterfactual_resource_cascade_remove_steps_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "cf_rc_rm.json"
    repdir = tmp_path / "rep_rc"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "resource_cascade",
            "--out",
            str(out_json),
            "--export-replay-dir",
            str(repdir),
            "--horizon",
            "11",
            "--remove",
            "0",
            "--seed",
            "66001",
            "--genome-seed",
            "66002",
            "--initial-overload",
            "0.065",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["meta"]["mode"] == "resource_cascade"
    assert payload["meta"]["domain"] == "resource_cascade"
    b = json.loads((repdir / "baseline.json").read_text(encoding="utf-8"))
    assert b["simulation_mode"] == "resource_cascade"


def test_export_counterfactual_resource_cascade_cascade_coupling_shift_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "cf_rc_cc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "resource_cascade",
            "--intervention",
            "cascade_coupling_shift",
            "--out",
            str(out_json),
            "--horizon",
            "10",
            "--seed",
            "66301",
            "--genome-seed",
            "66302",
            "--initial-overload",
            "0.06",
            "--variant-cascade-coupling",
            "0.38",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["intervention"] == "resource_cascade_cascade_coupling_shift"


def test_export_counterfactual_resource_cascade_overload_shift_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "cf_rc_io.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "resource_cascade",
            "--intervention",
            "initial_overload_shift",
            "--out",
            str(out_json),
            "--horizon",
            "10",
            "--seed",
            "66101",
            "--genome-seed",
            "66102",
            "--initial-overload",
            "0.06",
            "--variant-initial-overload",
            "0.13",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["intervention"] == "resource_cascade_initial_overload_shift"
    assert payload["delta_integral_instability"] is not None


def test_export_resource_cascade_joint_attribution_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "joint_rc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_resource_cascade_joint_attribution.py"),
            "--out",
            str(out_json),
            "--horizon",
            "10",
            "--seed",
            "66201",
            "--genome-seed",
            "66202",
            "--initial-overload",
            "0.07",
            "--variant-initial-overload",
            "0.11",
            "--remove",
            "0",
        ],
        check=True,
        cwd=str(ROOT),
    )
    merged = json.loads(out_json.read_text(encoding="utf-8"))
    assert merged["schema"] == "attribution-merge-v1"
    assert merged["branch_count"] == 2


def test_narrate_frozen_json_replay_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "narrate_frozen_json.py"),
            str(ROOT / "artifacts" / "replay_viewer" / "sample_resource_cascade_replay.json"),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert "resource_cascade" in proc.stdout
    assert "replay rollout" in proc.stdout


def test_narrate_frozen_json_cite_digest_cli(py_exe: str, tmp_path: Path) -> None:
    j = tmp_path / "x.json"
    j.write_text('{"schema_version": "0.4.0", "simulation_mode": "aggregate", "trajectory": []}', encoding="utf-8")
    out_j = tmp_path / "narr.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "narrate_frozen_json.py"),
            str(j),
            "--cite-digest",
            "--json-out",
            str(out_j),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_j.read_text(encoding="utf-8"))
    assert payload["schema"] == "narration-summary-v1"
    assert len(payload["input_sha256"]) == 64
    assert "citation_sha256:" in payload["text"]


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
    assert b["meta"]["intervention"] == "remove_steps"


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
    assert "metric_notes" in out
    assert "peg ratio" in out["metric_notes"]["left_price_metric"].lower()
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


def test_run_resource_cascade_ga_demo_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "rc_ga.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_resource_cascade_ga_demo.py"),
            "--generations",
            "2",
            "--population-size",
            "8",
            "--seed",
            "919",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "resource_cascade"
    assert data["meta"]["cli"] == "run_resource_cascade_ga_demo"
    assert data["meta"]["domain"] == "resource_cascade"
    assert data["trajectory"]


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
    proc3 = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--mode",
            "resource_cascade",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--max-steps",
            "14",
            "--horizon",
            "9",
            "--initial-overload",
            "0.06",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    rc = json.loads(proc3.stdout)
    assert rc["mode"] == "resource_cascade"
    assert rc["initial_overload"] == pytest.approx(0.06)
    assert rc["nodes"] is None


def test_export_replay_resource_cascade_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "rc_rep.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "resource_cascade",
            "--out",
            str(out),
            "--horizon",
            "11",
            "--seed",
            "331",
            "--genome-seed",
            "332",
            "--initial-overload",
            "0.07",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "resource_cascade"
    assert data["meta"]["cli"] == "export_replay"
    assert data["meta"]["domain"] == "resource_cascade"
    assert data["meta"]["initial_overload"] == pytest.approx(0.07)


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


def test_export_pareto_front_network_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "pf_net.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_pareto_front.py"),
            "--mode",
            "network",
            "--out",
            str(out),
            "--nodes",
            "14",
            "--horizon",
            "10",
            "--generations",
            "2",
            "--population-size",
            "10",
            "--max-steps",
            "22",
            "--seed",
            "414141",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "pareto-front-v1"
    assert "topology" in data
    assert data["topology"]["kind"] == "erdos_renyi"


def test_run_coevolution_resource_cascade_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "coev_rc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "resource_cascade",
            "--rounds",
            "1",
            "--max-steps",
            "30",
            "--initial-overload",
            "0.06",
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
            "707707",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "resource_cascade"
    assert data["meta"]["coevolution_mode"] == "resource_cascade"


def test_export_pareto_front_resource_cascade_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "pf_rc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_pareto_front.py"),
            "--mode",
            "resource_cascade",
            "--out",
            str(out),
            "--initial-overload",
            "0.07",
            "--horizon",
            "10",
            "--generations",
            "2",
            "--population-size",
            "10",
            "--max-steps",
            "24",
            "--seed",
            "616616",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "pareto-front-v1"
    assert data["domain"] == "resource_cascade"
    assert data["initial_overload"] == pytest.approx(0.07)


def test_export_pareto_front_neighbor_json_smoke(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "ring.json"
    nb.write_text("[[1],[0]]", encoding="utf-8")
    out = tmp_path / "pf_nl.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_pareto_front.py"),
            "--mode",
            "network",
            "--neighbor-json",
            str(nb),
            "--out",
            str(out),
            "--horizon",
            "8",
            "--generations",
            "2",
            "--population-size",
            "8",
            "--max-steps",
            "16",
            "--seed",
            "303030",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["topology"]["storage"] == "neighbor_lists"
    assert data["topology"]["n_nodes"] == 2


def test_export_counterfactual_neighbor_json_writes_replays(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "nl.json"
    nb.write_text("[[1],[0]]", encoding="utf-8")
    out_json = tmp_path / "cf_nl.json"
    repdir = tmp_path / "rep_nl"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "network",
            "--neighbor-json",
            str(nb),
            "--out",
            str(out_json),
            "--export-replay-dir",
            str(repdir),
            "--horizon",
            "10",
            "--remove",
            "0",
            "--seed",
            "55",
            "--genome-seed",
            "56",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["meta"]["topology"]["storage"] == "neighbor_lists"
    b = json.loads((repdir / "baseline.json").read_text(encoding="utf-8"))
    assert b["simulation_mode"] == "network"


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


def test_run_benchmark_suite_validate_cli(py_exe: str) -> None:
    subprocess.run(
        [py_exe, str(ROOT / "scripts" / "run_benchmark_suite.py"), "--validate"],
        check=True,
        cwd=str(ROOT),
    )


def test_export_counterfactual_base_panic_shift_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_bp.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "network",
            "--nodes",
            "14",
            "--horizon",
            "11",
            "--intervention",
            "base_panic_shift",
            "--base-panic",
            "0.06",
            "--variant-base-panic",
            "0.17",
            "--seed",
            "8801",
            "--genome-seed",
            "22",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["meta"]["intervention"] == "base_panic_shift"
    assert payload["intervention"] == "network_base_panic_shift"


def test_export_counterfactual_beta_shift_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_b.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "network",
            "--nodes",
            "13",
            "--horizon",
            "10",
            "--intervention",
            "contagion_beta_shift",
            "--beta",
            "0.4",
            "--variant-beta",
            "0.1",
            "--seed",
            "8802",
            "--genome-seed",
            "23",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["meta"]["intervention"] == "contagion_beta_shift"
    assert payload["intervention"] == "network_contagion_beta_shift"


def test_export_counterfactual_edge_weight_shift_cli(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "nl_ew.json"
    nb.write_text("[[1],[0]]", encoding="utf-8")
    out = tmp_path / "cf_ew.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "network",
            "--neighbor-json",
            str(nb),
            "--horizon",
            "9",
            "--intervention",
            "edge_weight_shift",
            "--edge-from",
            "0",
            "--edge-to",
            "1",
            "--variant-edge-weight",
            "3.5",
            "--seed",
            "8805",
            "--genome-seed",
            "29",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["meta"]["intervention"] == "edge_weight_shift"
    assert payload["intervention"] == "network_neighbor_edge_weight_shift"


def test_export_counterfactual_chain_cli(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "nl_chain.json"
    nb.write_text("[[1],[0]]", encoding="utf-8")
    spec = tmp_path / "chain.json"
    spec.write_text(
        '{"schema": "network-mutation-chain-spec-v1", "steps": ['
        '{"kind": "contagion_beta", "value": 0.15}, '
        '{"kind": "edge_weight", "from": 0, "to": 1, "weight": 3.0}'
        "]}",
        encoding="utf-8",
    )
    out = tmp_path / "cf_chain.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual_chain.py"),
            "--chain-json",
            str(spec),
            "--neighbor-json",
            str(nb),
            "--horizon",
            "9",
            "--seed",
            "9101",
            "--genome-seed",
            "51",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "network_mutation_chain"
    assert len(payload["mutation_steps"]) == 2
    assert payload["path_trace"]["schema"] == "explanation-mutation-chain-path-v1"
    assert len(payload["path_trace"]["edges"]) == 2


def test_merge_counterfactual_attribution_cli(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "nl_merge.json"
    nb.write_text("[[1],[0]]", encoding="utf-8")
    common = [
        py_exe,
        str(ROOT / "scripts" / "export_counterfactual.py"),
        "--mode",
        "network",
        "--neighbor-json",
        str(nb),
        "--horizon",
        "8",
        "--base-panic",
        "0.06",
        "--seed",
        "7701",
        "--genome-seed",
        "31",
    ]
    a = tmp_path / "cf_a.json"
    subprocess.run(
        [
            *common,
            "--intervention",
            "base_panic_shift",
            "--base-panic",
            "0.06",
            "--variant-base-panic",
            "0.14",
            "--out",
            str(a),
        ],
        check=True,
        cwd=str(ROOT),
    )
    b = tmp_path / "cf_b.json"
    subprocess.run(
        [
            *common,
            "--intervention",
            "edge_weight_shift",
            "--edge-from",
            "0",
            "--edge-to",
            "1",
            "--variant-edge-weight",
            "2.0",
            "--out",
            str(b),
        ],
        check=True,
        cwd=str(ROOT),
    )
    merged_path = tmp_path / "merged.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "merge_counterfactual_attribution.py"),
            "--inputs",
            str(a),
            str(b),
            "--out",
            str(merged_path),
        ],
        check=True,
        cwd=str(ROOT),
    )
    merged = json.loads(merged_path.read_text(encoding="utf-8"))
    assert merged["schema"] == "attribution-merge-v1"
    assert merged["branch_count"] == 2
    assert len(merged["edges"]) == 2


def test_summarize_attribution_merge_cli(py_exe: str, tmp_path: Path) -> None:
    merged_path = tmp_path / "merge_min.json"
    merged_path.write_text(
        json.dumps(
            {
                "schema": "attribution-merge-v1",
                "strict_baseline": True,
                "branch_count": 1,
                "nodes": [],
                "edges": [
                    {
                        "from": "baseline",
                        "to": "branch_0",
                        "intervention": "t",
                        "delta_integral_instability": -0.5,
                        "delta_attack_cost": 0.25,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "inter_summary.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "summarize_attribution_merge.py"),
            "--input",
            str(merged_path),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    s = json.loads(out.read_text(encoding="utf-8"))
    assert s["schema"] == "attribution-interaction-summary-v1"
    assert s["sum_branch_delta_integral_instability"] == -0.5


def test_export_counterfactual_edge_weights_shift_cli(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "nl_multi.json"
    nb.write_text("[[1,2],[0],[0]]", encoding="utf-8")
    patch = tmp_path / "patch.json"
    patch.write_text(
        json.dumps(
            [
                {"from": 0, "to": 1, "weight": 4.0},
                {"from": 0, "to": 2, "weight": 0.8},
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "cf_multi.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "network",
            "--neighbor-json",
            str(nb),
            "--horizon",
            "9",
            "--intervention",
            "edge_weights_shift",
            "--edges-patch-json",
            str(patch),
            "--seed",
            "8806",
            "--genome-seed",
            "30",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "network_neighbor_edges_weight_patch"
    assert len(payload["edges_patch"]) == 2


def test_run_benchmark_manifest_out_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "manifest.json"
    subprocess.run(
        [py_exe, str(ROOT / "scripts" / "run_benchmark_suite.py"), "--manifest-out", str(out)],
        check=True,
        cwd=str(ROOT),
    )
    m = json.loads(out.read_text(encoding="utf-8"))
    assert m["schema"] == "benchmark-manifest-v1"
    assert m["bundle_count"] >= 3


def test_frozen_json_digest_cli(py_exe: str, tmp_path: Path) -> None:
    j = tmp_path / "blob.json"
    j.write_text('{"x": 1}', encoding="utf-8")
    proc = subprocess.run(
        [py_exe, str(ROOT / "scripts" / "frozen_json_digest.py"), str(j), "--json-out", str(tmp_path / "dig.json")],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert len(proc.stdout.strip()) > 10
    dig = json.loads((tmp_path / "dig.json").read_text(encoding="utf-8"))
    assert dig["schema"] == "frozen-json-digest-v1"
    assert len(dig["files"]) == 1


def test_counterfactual_epsilon_sweep_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "eps.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "network",
            "--axis",
            "base_panic",
            "--values",
            "0.05,0.11",
            "--nodes",
            "13",
            "--horizon",
            "10",
            "--rollout-seed",
            "9901",
            "--genome-seed",
            "42",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "counterfactual-epsilon-sweep-v1"
    assert data["summary"]["count"] == 2
    assert data["mode"] == "network"


def test_counterfactual_epsilon_sweep_edge_weight_cli(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "nl_eps_ew.json"
    nb.write_text("[[1],[0]]", encoding="utf-8")
    out = tmp_path / "eps_ew.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "network",
            "--axis",
            "edge_weight",
            "--values",
            "0.25,1.0,4.0",
            "--neighbor-json",
            str(nb),
            "--edge-from",
            "0",
            "--edge-to",
            "1",
            "--horizon",
            "9",
            "--rollout-seed",
            "9905",
            "--genome-seed",
            "44",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["axis"] == "edge_weight"
    assert data["summary"]["count"] == 3


def test_counterfactual_epsilon_sweep_resource_cascade_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "eps_rc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "resource_cascade",
            "--axis",
            "initial_overload",
            "--values",
            "0.05,0.09,0.13",
            "--horizon",
            "10",
            "--rollout-seed",
            "99331",
            "--genome-seed",
            "99332",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "counterfactual-epsilon-sweep-v1"
    assert data["mode"] == "resource_cascade"
    assert data["axis"] == "initial_overload"
    assert data["summary"]["count"] == 3


def test_counterfactual_epsilon_sweep_aggregate_and_trace_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "eps_agg.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "aggregate",
            "--axis",
            "initial_panic",
            "--values",
            "0.05,0.08",
            "--horizon",
            "11",
            "--rollout-seed",
            "9903",
            "--genome-seed",
            "43",
            "--emit-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["axis"] == "initial_panic"
    assert data["mode"] == "aggregate"
    assert "trace" in data
    assert data["trace"]["schema"] == "explanation-trace-v1"
    assert len(data["trace"]["edges"]) == 1


def test_fragility_robustness_sweep_json_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--graph-seeds",
            "101,102",
            "--nodes",
            "12",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-robustness-ensemble-v1"
    assert data["summary"]["count"] == 2
