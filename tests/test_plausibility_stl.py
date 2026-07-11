"""Unit tests for plausibility-search-v1 and stl-robustness-v1."""

from __future__ import annotations

import numpy as np

from fragility_engine.adversary.plausibility import (
    PLAUSIBILITY_SEARCH_SCHEMA,
    insanity_budget,
    plausibility_search_payload,
    plausible_search,
    schedule_log_likelihood,
)
from fragility_engine.byow.examples import get_example
from fragility_engine.falsify.examples import get_example as get_falsify_example
from fragility_engine.falsify.stl import (
    STL_ROBUSTNESS_SCHEMA,
    parse_stl,
    robustness,
    stl_falsify_search,
    stl_robustness_payload,
)
from fragility_engine.fel.conventions import SCHEMA_REGISTRY
from fragility_engine.types import TrajectoryStep


def test_schema_registry_flight2() -> None:
    assert SCHEMA_REGISTRY["plausibility_search"] == PLAUSIBILITY_SEARCH_SCHEMA
    assert SCHEMA_REGISTRY["stl_robustness"] == STL_ROBUSTNESS_SCHEMA


def test_quiet_genome_higher_likelihood() -> None:
    quiet = np.zeros((8, 2), dtype=np.float64)
    loud = np.ones((8, 2), dtype=np.float64) * 0.95
    assert schedule_log_likelihood(quiet) > schedule_log_likelihood(loud)
    assert insanity_budget(loud) > insanity_budget(quiet)


def test_plausible_search_smoke() -> None:
    spec = get_example("capacity-pool")
    world = spec.make_world()

    def evaluator(genome: np.ndarray, seed: int):
        return spec.rollout(world, genome, seed)

    psr = plausible_search(
        evaluator,
        horizon=spec.default_horizon,
        seed=7,
        generations=2,
        population_size=8,
        plausibility_weight=0.5,
    )
    payload = plausibility_search_payload(psr)
    assert payload["schema"] == PLAUSIBILITY_SEARCH_SCHEMA
    assert "insanity_budget" in payload
    assert payload["plausibility_weight"] == 0.5


def test_parse_stl_g_and_pred() -> None:
    phi = parse_stl("G[0,3] x[0] < 0.9")

    def _step(i: int, x: float) -> TrajectoryStep:
        return TrajectoryStep(
            timestep=i,
            state_vector=np.array([x]),
            events=(),
            agent_actions_summary={},
            metrics={},
        )

    steps = [_step(i, 0.5) for i in range(5)]
    assert robustness(phi, steps) > 0.0
    steps_bad = [_step(i, 0.95 if i == 2 else 0.1) for i in range(5)]
    assert robustness(phi, steps_bad) < 0.0


def test_stl_falsify_search_smoke() -> None:
    spec = get_falsify_example("ranked-store")
    world = spec.make_world()

    def evaluator(genome: np.ndarray, seed: int):
        return spec.rollout(world, genome, seed)

    res = stl_falsify_search(
        evaluator,
        "G[0,5] x[0] < 100",
        horizon=spec.default_horizon,
        seed=3,
        generations=2,
        population_size=8,
    )
    payload = stl_robustness_payload(res)
    assert payload["schema"] == STL_ROBUSTNESS_SCHEMA
    assert payload["formula"].startswith("G[")
