"""Tests for BYOW examples, CLI, and falsification harness (Phases R/S)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fragility_engine.adversary.search import genetic_search
from fragility_engine.byow.check import check_rollout_determinism
from fragility_engine.byow.examples.capacity_pool import make_world as make_pool
from fragility_engine.byow.examples.capacity_pool import rollout as pool_rollout
from fragility_engine.byow.examples.token_bucket import make_world as make_bucket
from fragility_engine.byow.examples.token_bucket import rollout as bucket_rollout
from fragility_engine.falsify.examples.ranked_store import make_world as make_ranked
from fragility_engine.falsify.examples.ranked_store import rollout as ranked_rollout


def test_capacity_pool_deterministic() -> None:
    world = make_pool()

    def fn(g, s):
        return pool_rollout(world, g, s)

    ok, _ = check_rollout_determinism(fn, seed=42)
    assert ok


def test_token_bucket_deterministic() -> None:
    world = make_bucket()

    def fn(g, s):
        return bucket_rollout(world, g, s)

    ok, _ = check_rollout_determinism(fn, seed=42)
    assert ok


def test_capacity_pool_ga_can_collapse() -> None:
    world = make_pool()

    def fn(g, s):
        return pool_rollout(world, g, s)

    search = genetic_search(fn, horizon=16, generations=8, population_size=24, seed=411)
    assert search.best_rollout.collapsed


def test_falsify_ranked_store_finds_violation() -> None:
    world = make_ranked()

    def fn(g, s):
        return ranked_rollout(world, g, s)

    search = genetic_search(fn, horizon=14, generations=10, population_size=24, seed=707)
    assert search.best_rollout.collapsed


def test_fragility_cli_help() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "fragility_engine.cli.main", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "search" in proc.stdout


def test_fragility_search_smoke(tmp_path: Path) -> None:
    out = tmp_path / "replay.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "fragility_engine.cli.main",
            "search",
            "--example",
            "capacity-pool",
            "--generations",
            "4",
            "--population-size",
            "12",
            "--export-replay",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["simulation_mode"] == "capacity_pool_example"
    assert data["meta"]["harness_kind"] == "dynamics_v1"


def test_fragility_falsify_search_smoke(tmp_path: Path) -> None:
    out = tmp_path / "falsify.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "fragility_engine.cli.main",
            "falsify",
            "search",
            "--example",
            "ranked-store",
            "--generations",
            "8",
            "--population-size",
            "20",
            "--export-replay",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["collapsed"] is True
    assert data["meta"]["harness_kind"] == "falsification_v1"
