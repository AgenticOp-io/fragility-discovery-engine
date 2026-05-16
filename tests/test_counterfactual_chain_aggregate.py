"""Aggregate peg cumulative mutation chains (Phase I multi-knob)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual_chain_aggregate import (
    AGGREGATE_CHAIN_SPEC_SCHEMA,
    counterfactual_aggregate_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts_aggregate,
    parse_aggregate_chain_spec_payload,
)
from fragility_engine.explain.trace import (
    CHAIN_PATH_TRACE_AGGREGATE_SCHEMA,
    mutation_chain_path_to_trace_aggregate,
)
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "chains" / "aggregate_panic_depeg_chain.json"


def test_parse_aggregate_chain_spec_fixture() -> None:
    steps = parse_aggregate_chain_spec_payload(json.loads(FIXTURE.read_text(encoding="utf-8")))
    assert len(steps) == 2
    assert steps[0]["kind"] == "rumor_panic_gain"


def test_counterfactual_aggregate_mutation_chain_smoke() -> None:
    steps = parse_aggregate_chain_spec_payload(json.loads(FIXTURE.read_text(encoding="utf-8")))
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=24)
    genome = np.random.default_rng(11).uniform(size=(10, 2))
    report, base, var = counterfactual_aggregate_mutation_chain_with_rollouts(
        genome,
        template,
        steps=steps,
        rollout_seed=4401,
        initial_panic=0.05,
    )
    assert report["intervention"] == "aggregate_mutation_chain"
    assert len(report["mutation_steps"]) == 2
    assert base.simulation_mode == "aggregate"


def test_mutation_chain_path_trace_aggregate_shape() -> None:
    steps = parse_aggregate_chain_spec_payload(json.loads(FIXTURE.read_text(encoding="utf-8")))
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=22)
    genome = np.random.default_rng(12).uniform(size=(8, 2))
    path = mutation_chain_path_rollouts_aggregate(
        genome,
        template,
        steps=steps,
        rollout_seed=4402,
        initial_panic=0.06,
    )
    trace = mutation_chain_path_to_trace_aggregate(
        path,
        steps,
        rollout_seed=4402,
        baseline_initial_panic=0.06,
        variant_initial_panic=0.06,
    )
    assert trace["schema"] == CHAIN_PATH_TRACE_AGGREGATE_SCHEMA
    assert trace["source_chain_schema"] == AGGREGATE_CHAIN_SPEC_SCHEMA
    assert len(trace["nodes"]) == len(steps) + 1
