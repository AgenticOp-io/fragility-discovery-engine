"""Liquidity-ladder cumulative mutation chains (Phase N)."""

from __future__ import annotations

import numpy as np
import pytest

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual_chain_liquidity_ladder import (
    LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA,
    counterfactual_liquidity_ladder_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts_liquidity_ladder,
    parse_liquidity_ladder_chain_spec_payload,
)
from fragility_engine.explain.trace import (
    CHAIN_PATH_TRACE_LIQUIDITY_LADDER_SCHEMA,
    mutation_chain_path_to_trace_liquidity_ladder,
)
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld


def test_parse_liquidity_ladder_chain_spec_smoke():
    steps = parse_liquidity_ladder_chain_spec_payload(
        {
            "schema": LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA,
            "steps": [
                {"kind": "delever_rate", "value": 0.29},
                {"kind": "max_steps", "value": 34},
            ],
        }
    )
    assert len(steps) == 2
    assert steps[1]["value"] == 34


def test_mutation_chain_liquidity_ladder_path_trace_shape():
    template = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=18)
    genome = np.random.default_rng(3).uniform(size=(6, 2))
    steps = parse_liquidity_ladder_chain_spec_payload(
        {
            "schema": LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA,
            "steps": [{"kind": "haircut_damage", "value": 0.17}],
        }
    )
    rollouts = mutation_chain_path_rollouts_liquidity_ladder(
        genome, template, steps=steps, rollout_seed=991, initial_margin=0.06
    )
    trace = mutation_chain_path_to_trace_liquidity_ladder(
        rollouts, steps, rollout_seed=991, baseline_initial_margin=0.06, variant_initial_margin=0.06
    )
    assert trace["schema"] == CHAIN_PATH_TRACE_LIQUIDITY_LADDER_SCHEMA
    assert len(trace["nodes"]) == 2
    assert len(trace["edges"]) == 1


def test_mutation_chain_liquidity_ladder_empty_raises():
    template = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=12)
    genome = np.random.default_rng(2).uniform(size=(4, 2))
    with pytest.raises(ValueError, match="non-empty"):
        counterfactual_liquidity_ladder_mutation_chain_with_rollouts(
            genome, template, steps=[], rollout_seed=1, initial_margin=0.05
        )
