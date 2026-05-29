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


def test_export_counterfactual_service_backlog_remove_steps_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_sb_rm.json"
    rep = tmp_path / "rep_sb"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "service_backlog",
            "--horizon",
            "10",
            "--remove",
            "0,1",
            "--seed",
            "7701",
            "--genome-seed",
            "12",
            "--out",
            str(out),
            "--export-replay-dir",
            str(rep),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["meta"]["mode"] == "service_backlog"
    assert payload["meta"]["domain"] == "service_backlog"
    b = json.loads((rep / "baseline.json").read_text(encoding="utf-8"))
    assert b["simulation_mode"] == "service_backlog"


def test_export_counterfactual_service_backlog_process_rate_shift_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_sb_pr.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "service_backlog",
            "--horizon",
            "11",
            "--intervention",
            "process_rate_shift",
            "--initial-backlog",
            "0.06",
            "--variant-process-rate",
            "0.55",
            "--seed",
            "7702",
            "--genome-seed",
            "13",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "service_backlog_process_rate_shift"


def test_export_counterfactual_service_backlog_backlog_shift_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_sb_ib.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "service_backlog",
            "--horizon",
            "11",
            "--intervention",
            "initial_backlog_shift",
            "--initial-backlog",
            "0.07",
            "--variant-initial-backlog",
            "0.02",
            "--seed",
            "7703",
            "--genome-seed",
            "14",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "service_backlog_initial_backlog_shift"


def test_export_counterfactual_liquidity_ladder_remove_steps_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_ll_rm.json"
    rep = tmp_path / "rep_ll"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "liquidity_ladder",
            "--horizon",
            "10",
            "--remove",
            "0,1",
            "--seed",
            "7801",
            "--genome-seed",
            "24",
            "--initial-margin",
            "0.065",
            "--out",
            str(out),
            "--export-replay-dir",
            str(rep),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["meta"]["mode"] == "liquidity_ladder"
    assert payload["meta"]["domain"] == "liquidity_ladder"
    assert payload["meta"]["initial_margin"] == pytest.approx(0.065)
    b = json.loads((rep / "baseline.json").read_text(encoding="utf-8"))
    assert b["simulation_mode"] == "liquidity_ladder"
    assert b["meta"]["domain"] == "liquidity_ladder"
    assert b["meta"]["initial_margin"] == pytest.approx(0.065)


def test_export_counterfactual_liquidity_ladder_margin_shift_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_ll_im.json"
    rep = tmp_path / "rep_ll_im"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "liquidity_ladder",
            "--horizon",
            "11",
            "--intervention",
            "initial_margin_shift",
            "--initial-margin",
            "0.07",
            "--variant-initial-margin",
            "0.12",
            "--seed",
            "7802",
            "--genome-seed",
            "25",
            "--out",
            str(out),
            "--export-replay-dir",
            str(rep),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "liquidity_ladder_initial_margin_shift"
    c = json.loads((rep / "counterfactual.json").read_text(encoding="utf-8"))
    assert c["meta"]["baseline_initial_margin"] == pytest.approx(0.07)
    assert c["meta"]["variant_initial_margin"] == pytest.approx(0.12)


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
    assert merged["meta"]["second_branch"] == "initial_overload_shift"


def test_export_resource_cascade_joint_attribution_coupling_second_branch_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "joint_rc_cc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_resource_cascade_joint_attribution.py"),
            "--out",
            str(out_json),
            "--second-branch",
            "cascade_coupling_shift",
            "--variant-cascade-coupling",
            "0.41",
            "--horizon",
            "10",
            "--seed",
            "66301",
            "--genome-seed",
            "66302",
            "--initial-overload",
            "0.07",
            "--remove",
            "0",
        ],
        check=True,
        cwd=str(ROOT),
    )
    merged = json.loads(out_json.read_text(encoding="utf-8"))
    assert merged["schema"] == "attribution-merge-v1"
    assert merged["branch_count"] == 2
    assert merged["meta"]["second_branch"] == "cascade_coupling_shift"
    ivs = {e["intervention"] for e in merged["edges"]}
    assert "remove_steps" in ivs
    assert "resource_cascade_cascade_coupling_shift" in ivs


def test_export_resource_cascade_triple_attribution_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "triple_rc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_resource_cascade_triple_attribution.py"),
            "--out",
            str(out_json),
            "--horizon",
            "10",
            "--seed",
            "66401",
            "--genome-seed",
            "66402",
            "--initial-overload",
            "0.07",
            "--variant-initial-overload",
            "0.11",
            "--variant-cascade-coupling",
            "0.35",
            "--remove",
            "0",
        ],
        check=True,
        cwd=str(ROOT),
    )
    merged = json.loads(out_json.read_text(encoding="utf-8"))
    assert merged["schema"] == "attribution-merge-v1"
    assert merged["branch_count"] == 3
    assert merged["meta"]["branch_count"] == 3
    assert len(merged["edges"]) == 3


def test_narrate_frozen_json_service_backlog_replay_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "narrate_frozen_json.py"),
            str(ROOT / "artifacts" / "replay_viewer" / "sample_service_backlog_replay.json"),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "service_backlog" in proc.stdout.lower() or "backlog" in proc.stdout.lower()


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


def test_export_explanation_dag_from_counterfactual_cli(py_exe: str, tmp_path: Path) -> None:
    cf = tmp_path / "cf.json"
    cf.write_text(
        json.dumps(
            {
                "intervention": "remove_steps",
                "baseline": {"integral_instability": 3.0, "attack_cost": 1.0, "collapsed": True},
                "counterfactual": {"integral_instability": 1.0, "attack_cost": 1.0, "collapsed": False},
            },
        ),
        encoding="utf-8",
    )
    out = tmp_path / "dag.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_explanation_dag.py"),
            "--from-counterfactual",
            str(cf),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "explanation-dag-v1"
    assert data["kind"] == "counterfactual_pair"


def test_narrate_frozen_json_institutional_composite_cli(py_exe: str, tmp_path: Path) -> None:
    comp = tmp_path / "composite.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--nodes",
            "9",
            "--horizon",
            "6",
            "--out",
            str(comp),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    proc = subprocess.run(
        [py_exe, str(ROOT / "scripts" / "narrate_frozen_json.py"), str(comp)],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert "institutional composite" in proc.stdout
    assert "fragility-institutional-composite-v1" in proc.stdout


def test_narrate_frozen_json_institutional_composite_quad_cli(py_exe: str, tmp_path: Path) -> None:
    comp = tmp_path / "composite_quad.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--nodes",
            "9",
            "--horizon",
            "6",
            "--quad",
            "--out",
            str(comp),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    proc = subprocess.run(
        [py_exe, str(ROOT / "scripts" / "narrate_frozen_json.py"), str(comp)],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert "institutional composite" in proc.stdout
    assert "fragility-institutional-composite-v3" in proc.stdout
    assert "service_backlog:" in proc.stdout


def test_plot_replay_timeline_cli(py_exe: str, tmp_path: Path) -> None:
    png = tmp_path / "tl.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_replay_timeline.py"),
            str(ROOT / "artifacts" / "replay_viewer" / "sample_resource_cascade_replay.json"),
            "--out",
            str(png),
        ],
        check=True,
        cwd=str(ROOT),
    )
    raw = png.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(raw) > 2000


def test_plot_epsilon_sweep_cli(py_exe: str, tmp_path: Path) -> None:
    sweep_p = tmp_path / "sw.json"
    sweep_p.write_text(
        json.dumps(
            {
                "schema": "counterfactual-epsilon-sweep-v1",
                "axis": "initial_overload",
                "mode": "resource_cascade",
                "rollout_seed": 501,
                "runs": [
                    {
                        "initial_overload": 0.05,
                        "integral_instability": 2.1,
                        "collapsed": False,
                    },
                    {
                        "initial_overload": 0.14,
                        "integral_instability": 6.2,
                        "collapsed": True,
                    },
                ],
                "summary": {"count": 2},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    png = tmp_path / "eps.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_epsilon_sweep.py"),
            str(sweep_p),
            "--out",
            str(png),
        ],
        check=True,
        cwd=str(ROOT),
    )
    raw = png.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(raw) > 800


def test_plot_pareto_front_cli(py_exe: str, tmp_path: Path) -> None:
    png = tmp_path / "pf.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_pareto_front.py"),
            str(ROOT / "artifacts" / "pareto_viewer" / "sample_pareto_front.json"),
            "--out",
            str(png),
        ],
        check=True,
        cwd=str(ROOT),
    )
    raw = png.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(raw) > 1500


def test_plot_fragility_surface_csv_cli(py_exe: str, tmp_path: Path) -> None:
    csv_p = tmp_path / "surf.csv"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_surface.py"),
            "--out",
            str(csv_p),
            "--panic-points",
            "4",
            "--depeg-points",
            "4",
            "--steps",
            "12",
            "--seed",
            "555",
        ],
        check=True,
        cwd=str(ROOT),
    )
    png = tmp_path / "surf.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_fragility_surface_csv.py"),
            str(csv_p),
            "--out",
            str(png),
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_export_llm_narration_prompt_cli(py_exe: str, tmp_path: Path) -> None:
    bundle_p = tmp_path / "llm_bundle.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(ROOT / "artifacts" / "replay_viewer" / "sample_resource_cascade_replay.json"),
            "--cite-digest",
            "--out",
            str(bundle_p),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(bundle_p.read_text(encoding="utf-8"))
    assert data["schema"] == "llm-prompt-bundle-v1"
    assert data["template_id"] == "frozen_artifact_narration"
    assert data["prompt_pack"] == "narration_v1"
    assert data["template_version"]
    assert len(data["input_sha256"]) == 64
    assert "system_prompt" in data and "user_prompt" in data


def test_export_llm_narration_prompt_reviewer_pack_cli(py_exe: str, tmp_path: Path) -> None:
    bundle_p = tmp_path / "llm_rev.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(ROOT / "artifacts" / "replay_viewer" / "sample_resource_cascade_replay.json"),
            "--prompt-pack",
            "reviewer_memo_v1",
            "--out",
            str(bundle_p),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(bundle_p.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "reviewer_memo_v1"
    assert "sentences" in data["user_prompt"]


def test_export_llm_narration_prompt_status_digest_pack_cli(py_exe: str, tmp_path: Path) -> None:
    bundle_p = tmp_path / "llm_status.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(ROOT / "artifacts" / "replay_viewer" / "sample_resource_cascade_replay.json"),
            "--prompt-pack",
            "status_digest_v1",
            "--out",
            str(bundle_p),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(bundle_p.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "status_digest_v1"
    assert "checklist" in data["user_prompt"].lower() or "bullet" in data["user_prompt"].lower()


def test_plot_counterfactual_bars_cli(py_exe: str, tmp_path: Path) -> None:
    cf = tmp_path / "cf.json"
    cf.write_text(
        json.dumps(
            {
                "intervention": "remove_steps",
                "baseline": {"integral_instability": 5.2, "attack_cost": 3.1},
                "counterfactual": {"integral_instability": 2.3, "attack_cost": 3.4},
                "delta_integral_instability": 2.9,
                "delta_attack_cost": -0.3,
                "interpretation_hint": "test hint",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    png = tmp_path / "cfb.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_counterfactual_bars.py"),
            str(cf),
            "--out",
            str(png),
        ],
        check=True,
        cwd=str(ROOT),
    )
    raw = png.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(raw) > 600


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
    assert data["meta"]["eval_pool"] == "threads"
    assert data["meta"]["simulation_mode"] == "aggregate"


def test_run_mc_demo_network_mode_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "mc_net.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_mc_demo.py"),
            "--mode",
            "network",
            "--nodes",
            "14",
            "--samples",
            "6",
            "--horizon",
            "8",
            "--seed",
            "909",
            "--max-steps",
            "20",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "network"
    assert data["meta"]["cli"] == "run_mc_demo"
    assert data["meta"]["simulation_mode"] == "network"
    assert "topology" in data["meta"]


def test_run_mc_demo_service_backlog_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "mc_sb.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_mc_demo.py"),
            "--mode",
            "service_backlog",
            "--samples",
            "8",
            "--horizon",
            "9",
            "--seed",
            "9191",
            "--initial-backlog",
            "0.055",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "service_backlog"
    assert data["meta"]["initial_backlog"] == pytest.approx(0.055)


def test_run_mc_demo_liquidity_ladder_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "mc_ll.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_mc_demo.py"),
            "--mode",
            "liquidity_ladder",
            "--samples",
            "8",
            "--horizon",
            "9",
            "--seed",
            "9292",
            "--initial-margin",
            "0.064",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "liquidity_ladder"
    assert data["meta"]["simulation_mode"] == "liquidity_ladder"
    assert data["meta"]["initial_margin"] == pytest.approx(0.064)


def test_run_mc_demo_eval_workers_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "mc_par.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_mc_demo.py"),
            "--samples",
            "8",
            "--horizon",
            "10",
            "--seed",
            "505",
            "--eval-workers",
            "2",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["eval_workers"] == 2


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


def test_run_ga_demo_eval_workers_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "best.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_ga_demo.py"),
            "--generations",
            "2",
            "--population-size",
            "10",
            "--seed",
            "1001",
            "--eval-workers",
            "2",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["eval_workers"] == 2


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


def test_run_service_backlog_ga_demo_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "sb_ga.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_service_backlog_ga_demo.py"),
            "--generations",
            "2",
            "--population-size",
            "8",
            "--seed",
            "929",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "service_backlog"
    assert data["meta"]["cli"] == "run_service_backlog_ga_demo"
    assert data["meta"]["domain"] == "service_backlog"
    assert data["trajectory"]


def test_run_liquidity_ladder_ga_demo_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "ll_ga.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_liquidity_ladder_ga_demo.py"),
            "--generations",
            "2",
            "--population-size",
            "8",
            "--seed",
            "939",
            "--initial-margin",
            "0.066",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "liquidity_ladder"
    assert data["meta"]["cli"] == "run_liquidity_ladder_ga_demo"
    assert data["meta"]["domain"] == "liquidity_ladder"
    assert data["meta"]["initial_margin"] == pytest.approx(0.066)
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
    assert data["workflow"] == "ad_hoc"
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
    assert net["workflow"] == "ad_hoc"
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
    assert rc["workflow"] == "ad_hoc"
    assert rc["mode"] == "resource_cascade"
    assert rc["initial_overload"] == pytest.approx(0.06)
    assert rc["nodes"] is None
    rb = rc["resource_cascade_backend"]
    assert set(rb) == {"resource_cascade_backend_env", "resource_cascade_backend_effective"}
    assert rb["resource_cascade_backend_effective"] in ("numpy", "numba")

    proc_sb = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--mode",
            "service_backlog",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--max-steps",
            "14",
            "--horizon",
            "9",
            "--initial-backlog",
            "0.06",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    sb = json.loads(proc_sb.stdout)
    assert sb["workflow"] == "ad_hoc"
    assert sb["mode"] == "service_backlog"
    assert sb["initial_backlog"] == pytest.approx(0.06)
    assert sb["nodes"] is None
    assert "resource_cascade_backend" not in sb

    proc_b = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle",
            "aggregate_rollout_v1",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    bundle_payload = json.loads(proc_b.stdout)
    assert bundle_payload["workflow"] == "phase_h_bundle"
    assert bundle_payload["bundle_id"] == "aggregate_rollout_v1"
    assert bundle_payload["pinned_genome_seed"] == 9001
    assert bundle_payload["pinned_rollout_seed"] == 4242
    assert bundle_payload["mean_ms_per_rollout"] >= 0.0
    assert "resource_cascade_backend" not in bundle_payload

    proc_search = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle",
            "aggregate_rollout_v1",
            "--bench-search",
            "ga",
            "--eval-workers",
            "2",
            "--search-generations",
            "1",
            "--search-population",
            "8",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    search_payload = json.loads(proc_search.stdout)
    assert search_payload["workflow"] == "phase_h_bundle_search_microbench"
    assert search_payload["bench_search"] == "ga"
    assert search_payload["eval_workers"] == 2
    assert len(search_payload["bundles"]) == 1
    assert search_payload["bundles"][0]["bundle_id"] == "aggregate_rollout_v1"

    proc_search_mc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle",
            "aggregate_rollout_v1",
            "--bench-search",
            "mc",
            "--search-samples",
            "6",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    mc_pl = json.loads(proc_search_mc.stdout)
    assert mc_pl["workflow"] == "phase_h_bundle_search_microbench"
    assert mc_pl["bench_search"] == "mc"
    assert mc_pl["search_samples"] == 6

    bad = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bench-search",
            "ga",
            "--repeat",
            "1",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert bad.returncode == 2

    proc_proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle",
            "aggregate_rollout_v1",
            "--bench-search",
            "ga",
            "--eval-pool",
            "processes",
            "--eval-workers",
            "2",
            "--search-generations",
            "1",
            "--search-population",
            "8",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    proc_pl = json.loads(proc_proc.stdout)
    assert proc_pl["eval_pool"] == "processes"

    proc_rc_b = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle",
            "resource_cascade_rollout_v1",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    rc_bundle = json.loads(proc_rc_b.stdout)
    assert rc_bundle["bundle_id"] == "resource_cascade_rollout_v1"
    assert rc_bundle["resource_cascade_backend"]["resource_cascade_backend_effective"] in ("numpy", "numba")

    proc_sb_b = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle",
            "service_backlog_rollout_v1",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    sb_bundle = json.loads(proc_sb_b.stdout)
    assert sb_bundle["bundle_id"] == "service_backlog_rollout_v1"
    assert "resource_cascade_backend" not in sb_bundle


def test_benchmark_rollout_bundle_all_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle-all",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    suite = json.loads(proc.stdout)
    assert suite["workflow"] == "phase_h_bundle_suite"
    assert suite["bundle_count"] == 7
    assert len(suite["bundles"]) == 7
    ids = [row["bundle_id"] for row in suite["bundles"]]
    assert ids == sorted(ids)
    assert suite["total_wall_clock_s"] >= 0.0
    assert suite["resource_cascade_backend"]["resource_cascade_backend_effective"] in ("numpy", "numba")


def test_benchmark_rollout_liquidity_ladder_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--mode",
            "liquidity_ladder",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--max-steps",
            "14",
            "--horizon",
            "9",
            "--initial-margin",
            "0.067",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["workflow"] == "ad_hoc"
    assert data["mode"] == "liquidity_ladder"
    assert data["initial_margin"] == pytest.approx(0.067)
    assert data["nodes"] is None


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


def test_export_replay_service_backlog_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "sb_rep.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "service_backlog",
            "--out",
            str(out),
            "--horizon",
            "11",
            "--seed",
            "441",
            "--genome-seed",
            "442",
            "--initial-backlog",
            "0.07",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "service_backlog"
    assert data["meta"]["cli"] == "export_replay"
    assert data["meta"]["domain"] == "service_backlog"
    assert data["meta"]["initial_backlog"] == pytest.approx(0.07)


def test_export_replay_liquidity_ladder_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "ll_rep.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "liquidity_ladder",
            "--out",
            str(out),
            "--horizon",
            "11",
            "--seed",
            "551",
            "--genome-seed",
            "552",
            "--initial-margin",
            "0.072",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "liquidity_ladder"
    assert data["meta"]["cli"] == "export_replay"
    assert data["meta"]["domain"] == "liquidity_ladder"
    assert data["meta"]["initial_margin"] == pytest.approx(0.072)


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
    assert data["eval_workers"] == 1
    assert "topology" in data
    assert data["topology"]["kind"] == "erdos_renyi"


def test_export_pareto_front_payload_eval_workers_parallel(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "pf_ew.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_pareto_front.py"),
            "--mode",
            "aggregate",
            "--out",
            str(out),
            "--horizon",
            "8",
            "--generations",
            "1",
            "--population-size",
            "8",
            "--max-steps",
            "20",
            "--seed",
            "717171",
            "--eval-workers",
            "2",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["eval_workers"] == 2


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


def test_run_coevolution_service_backlog_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "coev_sb.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "service_backlog",
            "--rounds",
            "1",
            "--max-steps",
            "30",
            "--initial-backlog",
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
            "808808",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "service_backlog"
    assert data["meta"]["coevolution_mode"] == "service_backlog"


def test_run_coevolution_liquidity_ladder_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "coev_ll.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "liquidity_ladder",
            "--rounds",
            "1",
            "--max-steps",
            "30",
            "--initial-margin",
            "0.065",
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
            "818818",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "liquidity_ladder"
    assert data["meta"]["coevolution_mode"] == "liquidity_ladder"
    assert data["meta"]["initial_margin"] == pytest.approx(0.065)


def test_run_coevolution_inventory_buffer_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "coev_ib.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_coevolution.py"),
            "--mode",
            "inventory_buffer",
            "--rounds",
            "1",
            "--max-steps",
            "30",
            "--initial-stock",
            "0.85",
            "--attacker-generations",
            "2",
            "--attacker-population",
            "8",
            "--defender-generations",
            "2",
            "--defender-population",
            "7",
            "--seed",
            "818819",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "inventory_buffer"
    assert data["meta"]["coevolution_mode"] == "inventory_buffer"
    assert data["meta"]["initial_stock"] == pytest.approx(0.85)


def test_export_counterfactual_inventory_buffer_remove_steps_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_ib.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "inventory_buffer",
            "--intervention",
            "remove_steps",
            "--remove",
            "0,1",
            "--horizon",
            "12",
            "--seed",
            "99101",
            "--initial-stock",
            "0.88",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["domain"] == "inventory_buffer"


def test_export_inventory_buffer_counterfactual_chain_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cf_ib_chain.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_inventory_buffer_counterfactual_chain.py"),
            "--variant-initial-stock",
            "0.55",
            "--horizon",
            "12",
            "--seed",
            "99102",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["initial_stock"] == pytest.approx(0.88)


def test_export_inventory_buffer_mutation_chain_cli(py_exe: str, tmp_path: Path) -> None:
    spec = tmp_path / "ib_chain.json"
    spec.write_text(
        '{"schema": "inventory-buffer-mutation-chain-spec-v1", "steps": ['
        '{"kind": "demand_spike_gain", "value": 0.9}, '
        '{"kind": "fulfillment_erosion", "value": 0.2}'
        "]}",
        encoding="utf-8",
    )
    out = tmp_path / "cf_ib_mutation_chain.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_inventory_buffer_mutation_chain.py"),
            "--chain-json",
            str(spec),
            "--horizon",
            "10",
            "--max-steps",
            "24",
            "--seed",
            "99104",
            "--genome-seed",
            "54",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "inventory_buffer_mutation_chain"
    assert len(payload["mutation_steps"]) == 2
    assert payload["path_trace"]["schema"] == "explanation-mutation-chain-path-inventory-buffer-v1"
    assert len(payload["path_trace"]["edges"]) == 2


def test_counterfactual_epsilon_sweep_inventory_buffer_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "sweep_ib.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "inventory_buffer",
            "--axis",
            "initial_stock",
            "--values",
            "0.7,0.8,0.9",
            "--horizon",
            "12",
            "--rollout-seed",
            "99103",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["mode"] == "inventory_buffer"
    assert data["axis"] == "initial_stock"
    assert len(data["runs"]) == 3


def test_export_pareto_front_inventory_buffer_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "pf_ib.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_pareto_front.py"),
            "--mode",
            "inventory_buffer",
            "--initial-stock",
            "0.88",
            "--horizon",
            "10",
            "--generations",
            "2",
            "--population-size",
            "8",
            "--seed",
            "99104",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "pareto-front-v1"
    assert data["domain"] == "inventory_buffer"


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


def test_export_pareto_front_service_backlog_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "pf_sb.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_pareto_front.py"),
            "--mode",
            "service_backlog",
            "--out",
            str(out),
            "--initial-backlog",
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
            "626626",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "pareto-front-v1"
    assert data["domain"] == "service_backlog"
    assert data["initial_backlog"] == pytest.approx(0.07)


def test_export_pareto_front_liquidity_ladder_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "pf_ll.json"
    replay = tmp_path / "pf_ll_replay.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_pareto_front.py"),
            "--mode",
            "liquidity_ladder",
            "--out",
            str(out),
            "--export-replay",
            str(replay),
            "--initial-margin",
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
            "636636",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "pareto-front-v1"
    assert data["domain"] == "liquidity_ladder"
    assert data["initial_margin"] == pytest.approx(0.07)
    replay_data = json.loads(replay.read_text(encoding="utf-8"))
    assert replay_data["simulation_mode"] == "liquidity_ladder"
    assert replay_data["meta"]["initial_margin"] == pytest.approx(0.07)


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


def test_run_benchmark_suite_bench_search_json(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_benchmark_suite.py"),
            "--bench-search",
            "ga",
            "--eval-workers",
            "2",
            "--search-generations",
            "1",
            "--search-population",
            "8",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["workflow"] == "phase_h_bundle_search_microbench"
    assert data["eval_pool"] == "threads"
    assert len(data["bundles"]) == 7


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


def test_export_counterfactual_chain_base_panic_step_cli(py_exe: str, tmp_path: Path) -> None:
    nb = tmp_path / "nl_bp.json"
    nb.write_text("[[1],[0]]", encoding="utf-8")
    spec = ROOT / "tests" / "fixtures" / "chains" / "network_contagion_base_panic_chain.json"
    out = tmp_path / "cf_chain_bp.json"
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
            "9102",
            "--genome-seed",
            "52",
            "--base-panic",
            "0.05",
            "--variant-base-panic",
            "0.99",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["variant_base_panic"] == 0.14
    assert payload["path_trace"]["variant_base_panic"] == 0.14
    kinds = [s["kind"] for s in payload["mutation_steps"]]
    assert kinds == ["contagion_beta", "base_panic"]


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


def test_export_resource_cascade_counterfactual_chain_cli(py_exe: str, tmp_path: Path) -> None:
    spec = tmp_path / "rc_chain.json"
    spec.write_text(
        '{"schema": "resource-cascade-mutation-chain-spec-v1", "steps": ['
        '{"kind": "cascade_coupling", "value": 0.44}, '
        '{"kind": "rumor_gain", "value": 0.29}'
        "]}",
        encoding="utf-8",
    )
    out = tmp_path / "cf_rc_chain.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_resource_cascade_counterfactual_chain.py"),
            "--chain-json",
            str(spec),
            "--horizon",
            "10",
            "--max-steps",
            "24",
            "--seed",
            "9103",
            "--genome-seed",
            "52",
            "--variant-initial-overload",
            "0.09",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "resource_cascade_mutation_chain"
    assert len(payload["mutation_steps"]) == 2
    assert payload["path_trace"]["schema"] == "explanation-mutation-chain-path-resource-cascade-v1"
    assert len(payload["path_trace"]["edges"]) == 2


def test_export_service_backlog_counterfactual_chain_cli(py_exe: str, tmp_path: Path) -> None:
    spec = tmp_path / "sb_chain.json"
    spec.write_text(
        '{"schema": "service-backlog-mutation-chain-spec-v1", "steps": ['
        '{"kind": "process_rate", "value": 0.44}, '
        '{"kind": "ingest_gain", "value": 0.29}'
        "]}",
        encoding="utf-8",
    )
    out = tmp_path / "cf_sb_chain.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_service_backlog_counterfactual_chain.py"),
            "--chain-json",
            str(spec),
            "--horizon",
            "10",
            "--max-steps",
            "24",
            "--seed",
            "9104",
            "--genome-seed",
            "53",
            "--variant-initial-backlog",
            "0.09",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "service_backlog_mutation_chain"
    assert len(payload["mutation_steps"]) == 2
    assert payload["path_trace"]["schema"] == "explanation-mutation-chain-path-service-backlog-v1"
    assert len(payload["path_trace"]["edges"]) == 2


def test_export_liquidity_ladder_counterfactual_chain_cli(py_exe: str, tmp_path: Path) -> None:
    spec = tmp_path / "ll_chain.json"
    spec.write_text(
        '{"schema": "liquidity-ladder-mutation-chain-spec-v1", "steps": ['
        '{"kind": "delever_rate", "value": 0.27}, '
        '{"kind": "haircut_damage", "value": 0.16}'
        "]}",
        encoding="utf-8",
    )
    out = tmp_path / "cf_ll_chain.json"
    rep = tmp_path / "ll_chain_replays"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_liquidity_ladder_counterfactual_chain.py"),
            "--chain-json",
            str(spec),
            "--horizon",
            "10",
            "--max-steps",
            "24",
            "--seed",
            "9106",
            "--genome-seed",
            "55",
            "--initial-margin",
            "0.06",
            "--variant-initial-margin",
            "0.09",
            "--emit-path-trace",
            "--export-replay-dir",
            str(rep),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "liquidity_ladder_mutation_chain"
    assert len(payload["mutation_steps"]) == 2
    assert payload["path_trace"]["schema"] == "explanation-mutation-chain-path-liquidity-ladder-v1"
    baseline = json.loads((rep / "baseline.json").read_text(encoding="utf-8"))
    assert baseline["simulation_mode"] == "liquidity_ladder"


def test_export_aggregate_counterfactual_chain_cli(py_exe: str, tmp_path: Path) -> None:
    spec = ROOT / "tests" / "fixtures" / "chains" / "aggregate_panic_depeg_chain.json"
    out = tmp_path / "cf_agg_chain.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_aggregate_counterfactual_chain.py"),
            "--chain-json",
            str(spec),
            "--horizon",
            "10",
            "--max-steps",
            "24",
            "--seed",
            "9105",
            "--genome-seed",
            "54",
            "--emit-path-trace",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["intervention"] == "aggregate_mutation_chain"
    assert len(payload["mutation_steps"]) == 2
    assert payload["path_trace"]["schema"] == "explanation-mutation-chain-path-aggregate-v1"
    assert len(payload["path_trace"]["edges"]) == 2


def test_export_service_backlog_joint_attribution_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "merge_sb_cli.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_service_backlog_joint_attribution.py"),
            "--out",
            str(out),
            "--horizon",
            "10",
            "--max-steps",
            "22",
            "--seed",
            "9201",
            "--genome-seed",
            "9202",
            "--initial-backlog",
            "0.07",
            "--variant-initial-backlog",
            "0.03",
            "--remove",
            "0",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema"] == "attribution-merge-v1"
    assert payload["branch_count"] == 2
    assert len(payload["edges"]) == 2


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
    assert m["schema"] == "benchmark-manifest-v2"
    assert m["bundle_count"] >= 3
    assert len(m["bundles"]) == m["bundle_count"]
    assert len(m["golden_metrics_sha256"]) == 64
    assert m["resource_cascade_backend"]["resource_cascade_backend_effective"] in ("numpy", "numba")


def test_run_benchmark_manifest_summary_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [py_exe, str(ROOT / "scripts" / "run_benchmark_suite.py"), "--manifest-summary"],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.stdout
    assert "benchmark_manifest_summary" in proc.stdout
    assert "golden_metrics_sha256=" in proc.stdout


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


def test_counterfactual_epsilon_sweep_service_backlog_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "eps_sb.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "service_backlog",
            "--axis",
            "initial_backlog",
            "--values",
            "0.04,0.08,0.12",
            "--horizon",
            "10",
            "--rollout-seed",
            "99441",
            "--genome-seed",
            "99442",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "counterfactual-epsilon-sweep-v1"
    assert data["mode"] == "service_backlog"
    assert data["axis"] == "initial_backlog"
    assert data["summary"]["count"] == 3


def test_counterfactual_epsilon_sweep_liquidity_ladder_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "eps_ll.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "liquidity_ladder",
            "--axis",
            "initial_margin",
            "--values",
            "0.04,0.08,0.12",
            "--horizon",
            "10",
            "--rollout-seed",
            "99551",
            "--genome-seed",
            "99552",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "counterfactual-epsilon-sweep-v1"
    assert data["mode"] == "liquidity_ladder"
    assert data["axis"] == "initial_margin"
    assert data["summary"]["count"] == 3


def test_counterfactual_epsilon_sweep_liquidity_ladder_delever_rate_cli(
    py_exe: str, tmp_path: Path
) -> None:
    out = tmp_path / "eps_ll_delever.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "liquidity_ladder",
            "--axis",
            "delever_rate",
            "--values",
            "0.08,0.16,0.24",
            "--initial-margin",
            "0.07",
            "--horizon",
            "10",
            "--rollout-seed",
            "99561",
            "--genome-seed",
            "99562",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "counterfactual-epsilon-sweep-v1"
    assert data["mode"] == "liquidity_ladder"
    assert data["axis"] == "delever_rate"
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
    assert data["topology_mode"] == "synthetic_er_ws"
    assert data["topology_representation"] == "dense"
    assert data["summary"]["count"] == 2


def test_fragility_robustness_sweep_neighbor_lists_json_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--topology",
            "neighbor_lists",
            "--graph-seeds",
            "101",
            "--nodes",
            "10",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["topology_representation"] == "neighbor_lists"
    assert data["runs"][0]["topology_representation"] == "neighbor_lists"


def test_fragility_robustness_sweep_1d_sensitivity_json_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--graph-seeds",
            "101,102",
            "--nodes",
            "12",
            "--sweep-param",
            "base_panic",
            "--sweep-values",
            "0.04,0.07",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-robustness-sensitivity-1d-v1"
    assert data["sweep_param"] == "base_panic"
    assert len(data["points"]) == 2


def test_fragility_robustness_sweep_2d_grid_json_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--graph-seeds",
            "101",
            "--nodes",
            "10",
            "--sweep-param",
            "whale_frac",
            "--sweep-values",
            "0.2,0.25",
            "--sweep-param-2",
            "base_panic",
            "--sweep-values-2",
            "0.04,0.06",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-robustness-sensitivity-2d-v1"
    assert data["summary"]["grid_cells"] == 4


def test_fragility_robustness_sweep_ga_population_1d_json_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--ga-population-sweep",
            "--ga-population-values",
            "10,12",
            "--ga-fixed-generations",
            "2",
            "--graph-seeds",
            "101,102",
            "--nodes",
            "10",
            "--horizon",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-robustness-ga-population-1d-v1"
    assert len(data["points"]) == 2


def test_fragility_robustness_sweep_ga_budget_2d_json_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--ga-budget-2d",
            "--ga-generations-values",
            "1,2",
            "--ga-population-values",
            "10,12",
            "--graph-seeds",
            "101,102",
            "--nodes",
            "10",
            "--horizon",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-robustness-ga-budget-2d-v1"
    assert len(data["points"]) == 4


def test_fragility_robustness_sweep_ga_budget_json_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--ga-budget-sweep",
            "--ga-generations-values",
            "1,2",
            "--ga-population-size",
            "10",
            "--graph-seeds",
            "101,102",
            "--nodes",
            "10",
            "--horizon",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-robustness-ga-budget-1d-v1"
    assert len(data["points"]) == 2


def test_mechanism_design_policy_sweep_json_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "mechanism_design_policy_sweep.py"),
            "--json",
            "--policies",
            "weak,reserve_focus",
            "--generations",
            "2",
            "--population-size",
            "10",
            "--horizon",
            "8",
            "--eval-workers",
            "4",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-mechanism-design-outer-v1"
    assert len(data["policies"]) == 2
    assert data["eval_workers"] == 4
    ps = data["policy_summary"]
    assert "inner_ga_best_fitness_min" in ps
    assert ps["policies_collapsed_count"] >= 0


@pytest.mark.parametrize(
    "extra,schema,required_keys",
    [
        pytest.param([], "fragility-institutional-composite-v1", (), id="twin"),
        pytest.param(
            ["--triple", "--aggregate-seed", "6001"],
            "fragility-institutional-composite-v2",
            ("aggregate",),
            id="triple",
        ),
        pytest.param(
            ["--quad", "--aggregate-seed", "6003", "--backlog-seed", "6004"],
            "fragility-institutional-composite-v3",
            ("aggregate", "service_backlog"),
            id="quad",
        ),
        pytest.param(
            [
                "--penta",
                "--aggregate-seed",
                "6007",
                "--backlog-seed",
                "6008",
                "--ladder-seed",
                "6009",
            ],
            "fragility-institutional-composite-v4",
            ("aggregate", "service_backlog", "liquidity_ladder"),
            id="penta",
        ),
    ],
)
def test_institutional_composite_demo_stdout_cli(
    py_exe: str,
    extra: list[str],
    schema: str,
    required_keys: tuple[str, ...],
) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--nodes",
            "9",
            "--horizon",
            "8",
            *extra,
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == schema
    for k in required_keys:
        assert k in data


@pytest.mark.parametrize(
    "extra,out_name,schema,required_keys",
    [
        pytest.param([], "composite.json", "fragility-institutional-composite-v1", (), id="twin-out"),
        pytest.param(
            ["--triple", "--aggregate-seed", "6002"],
            "composite_triple.json",
            "fragility-institutional-composite-v2",
            ("aggregate", "network", "resource_cascade"),
            id="triple-out",
        ),
        pytest.param(
            ["--quad", "--aggregate-seed", "6005", "--backlog-seed", "6006"],
            "composite_quad.json",
            "fragility-institutional-composite-v3",
            ("aggregate", "network", "resource_cascade", "service_backlog"),
            id="quad-out",
        ),
        pytest.param(
            [
                "--penta",
                "--aggregate-seed",
                "6010",
                "--backlog-seed",
                "6011",
                "--ladder-seed",
                "6012",
            ],
            "composite_penta.json",
            "fragility-institutional-composite-v4",
            (
                "aggregate",
                "network",
                "resource_cascade",
                "service_backlog",
                "liquidity_ladder",
            ),
            id="penta-out",
        ),
    ],
)
def test_institutional_composite_demo_out_cli(
    py_exe: str,
    tmp_path: Path,
    extra: list[str],
    out_name: str,
    schema: str,
    required_keys: tuple[str, ...],
) -> None:
    out_j = tmp_path / out_name
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--nodes",
            "9",
            "--horizon",
            "8",
            *extra,
            "--out",
            str(out_j),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    disk = json.loads(out_j.read_text(encoding="utf-8"))
    stdout = json.loads(proc.stdout)
    assert disk == stdout
    assert disk["schema"] == schema
    for k in required_keys:
        assert k in disk


def test_fragility_robustness_sweep_ga_population_neighbor_json_cli(py_exe: str, tmp_path: Path) -> None:
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text("[[1],[0]]", encoding="utf-8")
    b.write_text("[[1],[2],[0]]", encoding="utf-8")
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--ga-population-sweep",
            "--ga-population-values",
            "10,12",
            "--ga-fixed-generations",
            "2",
            "--neighbor-json-list",
            f"{a},{b}",
            "--horizon",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-robustness-ga-population-1d-v1"
    assert len(data["points"]) == 2
    assert data["points"][0]["ensemble"]["topology_mode"] == "neighbor_json_bundle"


def test_fragility_robustness_sweep_neighbor_json_list_cli(py_exe: str, tmp_path: Path) -> None:
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text("[[1],[0]]", encoding="utf-8")
    b.write_text("[[1],[2],[0]]", encoding="utf-8")
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_robustness_sweep.py"),
            "--json",
            "--neighbor-json-list",
            f"{a},{b}",
            "--horizon",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["topology_mode"] == "neighbor_json_bundle"
    assert data["summary"]["count"] == 2
    assert data["runs"][0]["topology_kind"] == "neighbor_json"


def test_export_fragility_certificate_cli(py_exe: str, tmp_path: Path) -> None:
    j = tmp_path / "x.json"
    j.write_text('{"k":1}', encoding="utf-8")
    out = tmp_path / "cert.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_fragility_certificate.py"),
            "--out",
            str(out),
            "--digest-json",
            str(j),
            "--no-manifest",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "fragility-certificate-v1"
    assert len(data["artifact_sha256"]) == 1


def test_run_flagship_demo_cli(py_exe: str, tmp_path: Path) -> None:
    out_dir = tmp_path / "flagship_out"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_flagship_demo.py"),
            "--out-dir",
            str(out_dir),
            "--skip-validate",
            "--generations",
            "1",
            "--population-size",
            "8",
            "--horizon",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
    )
    cert = json.loads((out_dir / "fragility_certificate.json").read_text(encoding="utf-8"))
    assert cert["schema"] == "fragility-certificate-v1"
    assert (out_dir / "best_replay.json").is_file()


def test_find_cheap_collapse_exports_replay_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cheap.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "find_cheap_collapse.py"),
            "--export-replay",
            str(out),
            "--eval-workers",
            "1",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["cli"] == "find_cheap_collapse"
    assert data["trajectory"]


def test_run_network_demo_exports_replay_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "net_ga.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_network_demo.py"),
            "--export-replay",
            str(out),
            "--nodes",
            "12",
            "--generations",
            "1",
            "--population-size",
            "8",
            "--horizon",
            "10",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "network"
    assert data["meta"]["cli"] == "run_network_demo"


def test_run_mc_demo_resource_cascade_smoke(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "mc_rc.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_mc_demo.py"),
            "--mode",
            "resource_cascade",
            "--samples",
            "6",
            "--horizon",
            "10",
            "--initial-overload",
            "0.06",
            "--export-replay",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "resource_cascade"


def test_export_counterfactual_aggregate_remove_steps_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "cf_agg_rm.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "aggregate",
            "--out",
            str(out_json),
            "--horizon",
            "12",
            "--remove",
            "0",
            "--seed",
            "77001",
            "--genome-seed",
            "77002",
            "--initial-panic",
            "0.05",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["meta"]["mode"] == "aggregate"


def test_export_minimized_replay_minimization_report_cli(py_exe: str, tmp_path: Path) -> None:
    replay = tmp_path / "min_replay.json"
    report = tmp_path / "min_report.json"
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_minimized_replay.py"),
            "--out",
            str(replay),
            "--minimization-report-out",
            str(report),
            "--horizon",
            "24",
            "--max-tries",
            "200",
            "--genome-search-seed",
            "17",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode == 2:
        pytest.skip("no collapsing schedule in random search window")
    assert proc.returncode == 0, proc.stderr
    assert report.is_file()
    rep = json.loads(report.read_text(encoding="utf-8"))
    assert "removed_indices" in rep or "minimal_genome" in rep


def test_export_explanation_dag_from_minimization_report_cli(py_exe: str, tmp_path: Path) -> None:
    report = tmp_path / "min_report.json"
    dag_out = tmp_path / "dag.json"
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_minimized_replay.py"),
            "--out",
            str(tmp_path / "min_replay.json"),
            "--minimization-report-out",
            str(report),
            "--horizon",
            "24",
            "--max-tries",
            "200",
            "--genome-search-seed",
            "19",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode == 2:
        pytest.skip("no collapsing schedule in random search window")
    assert proc.returncode == 0, proc.stderr
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_explanation_dag.py"),
            "--from-minimization-report",
            str(report),
            "--out",
            str(dag_out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    dag = json.loads(dag_out.read_text(encoding="utf-8"))
    assert dag["schema"] == "explanation-dag-v1"


def test_narrate_frozen_json_liquidity_ladder_replay_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "narrate_frozen_json.py"),
            str(ROOT / "artifacts" / "replay_viewer" / "sample_liquidity_ladder_replay.json"),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert "liquidity_ladder" in proc.stdout


def test_export_llm_narration_prompt_quad_pack_cli(py_exe: str, tmp_path: Path) -> None:
    composite = ROOT / "artifacts" / "composite_demo" / "sample_quad_composite.json"
    assert composite.is_file()
    out = tmp_path / "bundle.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(composite),
            "--prompt-pack",
            "institutional_composite_quad_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "llm-prompt-bundle-v1"
    assert data["prompt_pack"] == "institutional_composite_quad_v1"


def test_export_fragility_certificate_embeds_manifest_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cert.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_fragility_certificate.py"),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "fragility-certificate-v1"
    assert "benchmark_manifest" in data


def test_run_network_demo_neighbor_json_cli(py_exe: str, tmp_path: Path) -> None:
    topo = tmp_path / "topo.json"
    topo.write_text("[[1],[0]]", encoding="utf-8")
    out = tmp_path / "net_nb.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_network_demo.py"),
            "--neighbor-json",
            str(topo),
            "--export-replay",
            str(out),
            "--generations",
            "1",
            "--population-size",
            "8",
            "--horizon",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "network"
    assert data["meta"].get("topology_kind") == "neighbor_json" or "neighbor" in str(data["meta"])


def test_export_liquidity_ladder_joint_attribution_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "merge_ll.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_liquidity_ladder_joint_attribution.py"),
            "--out",
            str(out_json),
            "--horizon",
            "11",
            "--seed",
            "69201",
            "--genome-seed",
            "69202",
            "--initial-margin",
            "0.07",
            "--variant-initial-margin",
            "0.02",
            "--remove",
            "0",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["schema"] == "attribution-merge-v1"
    assert payload["branch_count"] == 2
    assert payload["meta"]["second_branch"] == "initial_margin_shift"


def test_export_liquidity_ladder_joint_attribution_delever_second_branch_cli(
    py_exe: str, tmp_path: Path
) -> None:
    out_json = tmp_path / "merge_ll_dr.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_liquidity_ladder_joint_attribution.py"),
            "--out",
            str(out_json),
            "--second-branch",
            "delever_rate_shift",
            "--variant-delever-rate",
            "0.50",
            "--horizon",
            "11",
            "--seed",
            "69203",
            "--genome-seed",
            "69204",
            "--initial-margin",
            "0.07",
            "--remove",
            "0",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    interventions = {e["intervention"] for e in payload["edges"]}
    assert "remove_steps" in interventions
    assert "liquidity_ladder_delever_rate_shift" in interventions


def test_export_llm_narration_prompt_liquidity_replay_pack_cli(py_exe: str, tmp_path: Path) -> None:
    replay = ROOT / "artifacts" / "replay_viewer" / "sample_liquidity_ladder_replay.json"
    out = tmp_path / "ll_bundle.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(replay),
            "--prompt-pack",
            "liquidity_ladder_replay_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "liquidity_ladder_replay_v1"
    assert "liquidity_ladder" in data["user_prompt"]


def test_export_llm_narration_prompt_penta_composite_pack_cli(py_exe: str, tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--penta",
            "--nodes",
            "9",
            "--horizon",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    composite_path = tmp_path / "penta.json"
    composite_path.write_text(proc.stdout, encoding="utf-8")
    out = tmp_path / "penta_bundle.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(composite_path),
            "--prompt-pack",
            "institutional_composite_penta_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "institutional_composite_penta_v1"
    assert "liquidity_ladder" in data["user_prompt"]


def test_export_counterfactual_liquidity_ladder_delever_rate_shift_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "cf_ll_dr.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "liquidity_ladder",
            "--intervention",
            "delever_rate_shift",
            "--out",
            str(out_json),
            "--horizon",
            "10",
            "--seed",
            "77301",
            "--genome-seed",
            "77302",
            "--initial-margin",
            "0.07",
            "--variant-delever-rate",
            "0.48",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["intervention"] == "liquidity_ladder_delever_rate_shift"


def test_export_service_backlog_joint_attribution_process_rate_branch_cli(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "merge_sb_pr.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_service_backlog_joint_attribution.py"),
            "--out",
            str(out_json),
            "--second-branch",
            "process_rate_shift",
            "--variant-process-rate",
            "0.50",
            "--horizon",
            "11",
            "--seed",
            "77401",
            "--genome-seed",
            "77402",
            "--initial-backlog",
            "0.07",
            "--remove",
            "0",
        ],
        check=True,
        cwd=str(ROOT),
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["meta"]["second_branch"] == "process_rate_shift"
    interventions = {e["intervention"] for e in payload["edges"]}
    assert "service_backlog_process_rate_shift" in interventions


def test_counterfactual_epsilon_sweep_service_backlog_process_rate_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "eps_sb_pr.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "service_backlog",
            "--axis",
            "process_rate",
            "--values",
            "0.36,0.44",
            "--initial-backlog",
            "0.07",
            "--rollout-seed",
            "77501",
            "--horizon",
            "10",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["mode"] == "service_backlog"
    assert data["axis"] == "process_rate"


def test_week1_smoke_continue_after_collapse_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "w_cont.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "week1_smoke.py"),
            "--export-replay",
            str(out),
            "--continue-after-collapse",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["continue_after_collapse"] is True


def test_export_replay_liquidity_ladder_continue_after_collapse_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "ll_cont.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "liquidity_ladder",
            "--initial-margin",
            "0.07",
            "--horizon",
            "12",
            "--seed",
            "77601",
            "--continue-after-collapse",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["continue_after_collapse"] is True


def test_narrate_frozen_json_penta_composite_cli(py_exe: str) -> None:
    bundled = ROOT / "artifacts" / "composite_demo" / "sample_penta_composite.json"
    if not bundled.is_file():
        pytest.skip("bundled penta composite missing; run regenerate_bundled_viewer_samples.py")
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "narrate_frozen_json.py"),
            str(bundled),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert "fragility-institutional-composite-v4" in proc.stdout
    assert "liquidity_ladder" in proc.stdout


def test_plot_institutional_composite_bars_penta_bundled_cli(py_exe: str, tmp_path: Path) -> None:
    bundled = ROOT / "artifacts" / "composite_demo" / "sample_penta_composite.json"
    if not bundled.is_file():
        pytest.skip("bundled penta composite missing")
    out = tmp_path / "penta_bars.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_institutional_composite_bars.py"),
            str(bundled),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert out.stat().st_size > 100


def test_export_llm_narration_prompt_paper_appendix_quad_cli(py_exe: str, tmp_path: Path) -> None:
    quad = ROOT / "artifacts" / "composite_demo" / "sample_quad_composite.json"
    out = tmp_path / "appendix_bundle.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(quad),
            "--prompt-pack",
            "paper_appendix_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "paper_appendix_v1"
    assert data["schema"] == "llm-prompt-bundle-v1"


def test_export_fragility_certificate_validate_bundles_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "cert_val.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_fragility_certificate.py"),
            "--out",
            str(out),
            "--validate-bundles",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "fragility-certificate-v1"
    assert data["benchmark_validation"]["status"] == "passed"


def test_summarize_attribution_merge_liquidity_ladder_cli(py_exe: str, tmp_path: Path) -> None:
    merge_path = ROOT / "artifacts" / "attribution_viewer" / "sample_attribution_merge_liquidity_ladder.json"
    if not merge_path.is_file():
        pytest.skip("bundled liquidity merge missing")
    out = tmp_path / "summary.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "summarize_attribution_merge.py"),
            "--input",
            str(merge_path),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "attribution-interaction-summary-v1"


def test_export_counterfactual_liquidity_ladder_delever_export_replay_dir_cli(
    py_exe: str, tmp_path: Path
) -> None:
    out_json = tmp_path / "cf_ll_dr_pair.json"
    repdir = tmp_path / "pair"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--mode",
            "liquidity_ladder",
            "--intervention",
            "delever_rate_shift",
            "--out",
            str(out_json),
            "--export-replay-dir",
            str(repdir),
            "--horizon",
            "10",
            "--seed",
            "77701",
            "--genome-seed",
            "77702",
            "--initial-margin",
            "0.07",
            "--variant-delever-rate",
            "0.45",
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert (repdir / "baseline.json").is_file()
    base = json.loads((repdir / "baseline.json").read_text(encoding="utf-8"))
    assert base["simulation_mode"] == "liquidity_ladder"


def test_export_pareto_front_liquidity_replay_pareto_index_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "pf_idx.json"
    replay = tmp_path / "pf_idx_replay.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_pareto_front.py"),
            "--mode",
            "liquidity_ladder",
            "--out",
            str(out),
            "--export-replay",
            str(replay),
            "--replay-pareto-index",
            "0",
            "--initial-margin",
            "0.07",
            "--horizon",
            "8",
            "--generations",
            "1",
            "--population-size",
            "8",
            "--seed",
            "77801",
        ],
        check=True,
        cwd=str(ROOT),
    )
    arch = json.loads(out.read_text(encoding="utf-8"))["archive"]
    assert len(arch) >= 1
    assert json.loads(replay.read_text(encoding="utf-8"))["meta"]["pareto_index"] == 0


def test_export_replay_service_backlog_continue_after_collapse_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "sb_cont.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "service_backlog",
            "--initial-backlog",
            "0.07",
            "--horizon",
            "12",
            "--seed",
            "77901",
            "--continue-after-collapse",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["continue_after_collapse"] is True


def test_export_replay_resource_cascade_continue_after_collapse_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "rc_cont.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_replay.py"),
            "--mode",
            "resource_cascade",
            "--initial-overload",
            "0.06",
            "--horizon",
            "12",
            "--seed",
            "77902",
            "--continue-after-collapse",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["continue_after_collapse"] is True


def test_export_llm_narration_prompt_paper_appendix_penta_cli(py_exe: str, tmp_path: Path) -> None:
    penta = ROOT / "artifacts" / "composite_demo" / "sample_penta_composite.json"
    if not penta.is_file():
        pytest.skip("bundled penta composite missing")
    out = tmp_path / "appendix_penta.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(penta),
            "--prompt-pack",
            "paper_appendix_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "paper_appendix_v1"
    assert "fragility-institutional-composite-v4" in data["user_prompt"]


def test_summarize_attribution_merge_service_backlog_cli(py_exe: str, tmp_path: Path) -> None:
    merge_path = ROOT / "artifacts" / "attribution_viewer" / "sample_attribution_merge_service_backlog.json"
    if not merge_path.is_file():
        pytest.skip("bundled service_backlog merge missing")
    out = tmp_path / "sb_summary.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "summarize_attribution_merge.py"),
            "--input",
            str(merge_path),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "attribution-interaction-summary-v1"
    assert data["branch_count"] == 2


def test_export_fragility_certificate_digest_penta_composite_cli(py_exe: str, tmp_path: Path) -> None:
    penta = ROOT / "artifacts" / "composite_demo" / "sample_penta_composite.json"
    if not penta.is_file():
        pytest.skip("bundled penta composite missing")
    out = tmp_path / "cert_digest.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_fragility_certificate.py"),
            "--out",
            str(out),
            "--digest-json",
            str(penta),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "fragility-certificate-v1"
    assert len(data["artifact_sha256"]) == 1


def test_run_network_demo_eval_workers_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "net_ew.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_network_demo.py"),
            "--export-replay",
            str(out),
            "--nodes",
            "10",
            "--generations",
            "1",
            "--population-size",
            "8",
            "--horizon",
            "8",
            "--eval-workers",
            "2",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["eval_workers"] == 2


def test_plot_institutional_composite_bars_twin_bundled_cli(py_exe: str, tmp_path: Path) -> None:
    twin = ROOT / "artifacts" / "composite_demo" / "sample_twin_composite.json"
    out = tmp_path / "twin_bars.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_institutional_composite_bars.py"),
            str(twin),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert out.stat().st_size > 100


def test_frozen_json_digest_penta_composite_bundled_cli(py_exe: str, tmp_path: Path) -> None:
    penta = ROOT / "artifacts" / "composite_demo" / "sample_penta_composite.json"
    if not penta.is_file():
        pytest.skip("bundled penta composite missing")
    out = tmp_path / "penta_dig.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "frozen_json_digest.py"),
            str(penta),
            "--json-out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "frozen-json-digest-v1"
    assert len(data["files"]) == 1
    assert len(data["files"][0]["sha256"]) == 64


def test_narrate_frozen_json_aggregate_replay_bundled_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "narrate_frozen_json.py"),
            str(ROOT / "artifacts" / "replay_viewer" / "sample_replay.json"),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert "aggregate" in proc.stdout.lower()
    assert "replay rollout" in proc.stdout


def test_narrate_frozen_json_penta_composite_cite_digest_cli(py_exe: str, tmp_path: Path) -> None:
    penta = ROOT / "artifacts" / "composite_demo" / "sample_penta_composite.json"
    if not penta.is_file():
        pytest.skip("bundled penta composite missing")
    out = tmp_path / "penta_narr.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "narrate_frozen_json.py"),
            str(penta),
            "--cite-digest",
            "--json-out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "narration-summary-v1"
    assert len(data["input_sha256"]) == 64


def test_benchmark_rollout_liquidity_ladder_eval_pool_processes_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle",
            "liquidity_ladder_rollout_v1",
            "--bench-search",
            "ga",
            "--eval-pool",
            "processes",
            "--eval-workers",
            "2",
            "--search-generations",
            "1",
            "--search-population",
            "8",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["eval_pool"] == "processes"
    assert payload["bundles"][0]["bundle_id"] == "liquidity_ladder_rollout_v1"


def test_export_llm_narration_prompt_reviewer_memo_penta_cli(py_exe: str, tmp_path: Path) -> None:
    penta = ROOT / "artifacts" / "composite_demo" / "sample_penta_composite.json"
    if not penta.is_file():
        pytest.skip("bundled penta composite missing")
    out = tmp_path / "review_penta.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(penta),
            "--prompt-pack",
            "reviewer_memo_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "reviewer_memo_v1"
    assert "fragility-institutional-composite-v4" in data["user_prompt"]


def test_plot_pareto_front_liquidity_ladder_bundled_cli(py_exe: str, tmp_path: Path) -> None:
    src = ROOT / "artifacts" / "pareto_viewer" / "sample_pareto_liquidity_ladder.json"
    if not src.is_file():
        pytest.skip("bundled liquidity pareto missing")
    png = tmp_path / "pf_ll.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_pareto_front.py"),
            str(src),
            "--out",
            str(png),
        ],
        check=True,
        cwd=str(ROOT),
    )
    raw = png.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(raw) > 500


def test_run_liquidity_ladder_ga_demo_eval_workers_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "ll_ga_ew.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "run_liquidity_ladder_ga_demo.py"),
            "--export-replay",
            str(out),
            "--generations",
            "1",
            "--population-size",
            "8",
            "--eval-workers",
            "2",
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["eval_workers"] == 2


def test_benchmark_rollout_liquidity_ladder_bench_search_mc_cli(py_exe: str) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--bundle",
            "liquidity_ladder_rollout_v1",
            "--bench-search",
            "mc",
            "--search-samples",
            "4",
            "--repeat",
            "1",
            "--warmup",
            "0",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["bench_search"] == "mc"
    assert payload["bundles"][0]["bundle_id"] == "liquidity_ladder_rollout_v1"


def test_plot_replay_timeline_liquidity_ladder_bundled_cli(py_exe: str, tmp_path: Path) -> None:
    replay = ROOT / "artifacts" / "replay_viewer" / "sample_liquidity_ladder_replay.json"
    png = tmp_path / "ll_timeline.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_replay_timeline.py"),
            str(replay),
            "--out",
            str(png),
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert png.stat().st_size > 500


def test_counterfactual_epsilon_sweep_liquidity_ladder_continue_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "eps_ll_cont.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "counterfactual_epsilon_sweep.py"),
            "--mode",
            "liquidity_ladder",
            "--axis",
            "initial_margin",
            "--values",
            "0.05,0.09",
            "--horizon",
            "10",
            "--rollout-seed",
            "88001",
            "--genome-seed",
            "88002",
            "--continue-after-collapse",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["mode"] == "liquidity_ladder"
    assert data["meta"]["continue_after_collapse"] is True


def test_export_llm_narration_prompt_institution_composite_quad_bundled_cli(
    py_exe: str, tmp_path: Path
) -> None:
    quad = ROOT / "artifacts" / "composite_demo" / "sample_quad_composite.json"
    out = tmp_path / "inst_quad.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(quad),
            "--prompt-pack",
            "institution_composite_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "institution_composite_v1"
    assert "fragility-institutional-composite-v3" in data["user_prompt"]


def test_run_coupled_fork_demo_help(py_exe: str) -> None:
    subprocess.run(
        [py_exe, str(ROOT / "scripts" / "run_coupled_fork_demo.py"), "--help"],
        check=True,
        cwd=str(ROOT),
    )


def test_export_llm_narration_prompt_coupled_replay_pack_cli(py_exe: str, tmp_path: Path) -> None:
    replay = ROOT / "forks" / "coupled_institution" / "artifacts" / "sample_coupled_replay.json"
    out = tmp_path / "coupled_llm.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(replay),
            "--prompt-pack",
            "coupled_institution_replay_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "coupled_institution_replay_v1"
    assert "coupled_institution" in data["user_prompt"]


def test_export_llm_narration_prompt_coupled_mutation_chain_pack_cli(py_exe: str, tmp_path: Path) -> None:
    chain = ROOT / "forks" / "coupled_institution" / "artifacts" / "sample_coupled_mutation_chain.json"
    if not chain.is_file():
        pytest.skip("run scripts/regenerate_coupled_fork_artifacts.py first")
    out = tmp_path / "chain_llm.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(chain),
            "--prompt-pack",
            "coupled_institution_mutation_chain_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "coupled_institution_mutation_chain_v1"
    assert "mutation chain" in data["user_prompt"].lower()


def test_export_llm_narration_prompt_coupled_comparison_pack_cli(py_exe: str, tmp_path: Path) -> None:
    comp = ROOT / "forks" / "coupled_institution" / "artifacts" / "sample_coupling_comparison.json"
    out = tmp_path / "cmp_llm.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(comp),
            "--prompt-pack",
            "coupled_institution_comparison_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "coupled_institution_comparison_v1"


def test_export_llm_narration_prompt_coupled_sweep_pack_cli(py_exe: str, tmp_path: Path) -> None:
    sweep = ROOT / "forks" / "coupled_institution" / "artifacts" / "coupling_strength_sweep.json"
    out = tmp_path / "sweep_llm.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(sweep),
            "--prompt-pack",
            "coupled_institution_coupling_sweep_v1",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["prompt_pack"] == "coupled_institution_coupling_sweep_v1"
    assert "coupling" in data["user_prompt"].lower()


def test_export_coupled_fork_llm_prompts_batch_cli(py_exe: str, tmp_path: Path) -> None:
    out_dir = tmp_path / "llm_exports"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_coupled_fork_llm_prompts.py"),
            "--out-dir",
            str(out_dir),
            "--cite-digest",
        ],
        check=True,
        cwd=str(ROOT),
    )
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "coupled-fork-llm-exports-v1"
    assert manifest["bundle_count"] == 4
    for stem in (
        "sample_coupled_replay",
        "coupling_strength_sweep",
        "sample_coupling_comparison",
        "sample_coupled_mutation_chain",
    ):
        bundle = json.loads((out_dir / f"{stem}.llm_bundle.json").read_text(encoding="utf-8"))
        assert bundle["schema"] == "llm-prompt-bundle-v1"
        assert bundle.get("input_sha256")


def test_plot_coupling_sweep_cli(py_exe: str, tmp_path: Path) -> None:
    sweep_p = tmp_path / "coupling.json"
    sweep_p.write_text(
        json.dumps(
            {
                "schema": "coupled-institution-coupling-sweep-v1",
                "fixture": "tests/fixtures/pinned_rollout_schedule.json",
                "rollout_seed": 8801,
                "rows": [
                    {"coupling_strength": 0.0, "integral_instability": 4.0, "collapsed": False},
                    {"coupling_strength": 0.5, "integral_instability": 8.0, "collapsed": True},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    png = tmp_path / "coupling.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_coupling_sweep.py"),
            str(sweep_p),
            "--out",
            str(png),
        ],
        check=True,
        cwd=str(ROOT),
    )
    raw = png.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
