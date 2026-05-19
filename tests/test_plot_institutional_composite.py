"""Plot institutional composite branches."""

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

SAMPLE = ROOT / "artifacts" / "composite_demo" / "sample_quad_composite.json"


def test_plot_institutional_composite_bars_cli(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "bars.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_institutional_composite_bars.py"),
            str(SAMPLE),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert out.is_file() and out.stat().st_size > 100


def test_plot_institutional_composite_bars_triple_sample(py_exe: str, tmp_path: Path) -> None:
    triple = ROOT / "artifacts" / "composite_demo" / "sample_triple_composite.json"
    out = tmp_path / "triple_bars.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_institutional_composite_bars.py"),
            str(triple),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert out.stat().st_size > 100


def test_plot_institutional_composite_bars_penta_from_demo(py_exe: str, tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--penta",
            "--horizon",
            "8",
            "--nodes",
            "9",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    composite = tmp_path / "penta.json"
    composite.write_text(proc.stdout, encoding="utf-8")
    out = tmp_path / "penta_bars.png"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "plot_institutional_composite_bars.py"),
            str(composite),
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert out.stat().st_size > 100


def test_export_llm_prompt_institutional_composite_quad_pack(py_exe: str, tmp_path: Path) -> None:
    quad = ROOT / "artifacts" / "composite_demo" / "sample_quad_composite.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(quad),
            "--prompt-pack",
            "institutional_composite_quad_v1",
            "--out",
            str(tmp_path / "quad_bundle.json"),
        ],
        check=True,
        cwd=str(ROOT),
    )
    bundle = json.loads((tmp_path / "quad_bundle.json").read_text(encoding="utf-8"))
    assert bundle["prompt_pack"] == "institutional_composite_quad_v1"
    assert "service_backlog" in bundle["user_prompt"]


def test_export_llm_prompt_institutional_composite_twin_pack(py_exe: str, tmp_path: Path) -> None:
    twin = ROOT / "artifacts" / "composite_demo" / "sample_twin_composite.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(twin),
            "--prompt-pack",
            "institutional_composite_twin_v1",
            "--out",
            str(tmp_path / "twin_bundle.json"),
        ],
        check=True,
        cwd=str(ROOT),
    )
    bundle = json.loads((tmp_path / "twin_bundle.json").read_text(encoding="utf-8"))
    assert bundle["prompt_pack"] == "institutional_composite_twin_v1"


def test_export_llm_prompt_institutional_composite_triple_pack(py_exe: str, tmp_path: Path) -> None:
    triple = ROOT / "artifacts" / "composite_demo" / "sample_triple_composite.json"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(triple),
            "--prompt-pack",
            "institutional_composite_triple_v1",
            "--out",
            str(tmp_path / "triple_bundle.json"),
        ],
        check=True,
        cwd=str(ROOT),
    )
    bundle = json.loads((tmp_path / "triple_bundle.json").read_text(encoding="utf-8"))
    assert bundle["prompt_pack"] == "institutional_composite_triple_v1"
    assert "fragility-institutional-composite-v2" in bundle["user_prompt"]


def test_export_llm_prompt_institution_composite_pack(py_exe: str, tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_llm_narration_prompt.py"),
            str(SAMPLE),
            "--prompt-pack",
            "institution_composite_v1",
            "--out",
            str(tmp_path / "bundle.json"),
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    bundle = json.loads((tmp_path / "bundle.json").read_text(encoding="utf-8"))
    assert bundle["schema"] == "llm-prompt-bundle-v1"
    assert bundle["prompt_pack"] == "institution_composite_v1"
    assert proc.returncode == 0
