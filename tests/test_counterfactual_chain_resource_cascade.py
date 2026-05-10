"""Resource-cascade cumulative mutation chains (Phase J)."""

from __future__ import annotations

import numpy as np
import pytest

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual_chain_resource_cascade import (
    RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA,
    apply_resource_cascade_mutation_step,
    counterfactual_resource_cascade_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts_resource_cascade,
    parse_resource_cascade_chain_spec_payload,
)
from fragility_engine.explain.trace import (
    CHAIN_PATH_TRACE_RESOURCE_CASCADE_SCHEMA,
    mutation_chain_path_to_trace_resource_cascade,
)
from fragility_engine.world.resource_cascade import ResourceCascadeWorld


def test_parse_resource_cascade_chain_spec_smoke():
    steps = parse_resource_cascade_chain_spec_payload(
        {
            "schema": RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA,
            "steps": [
                {"kind": "cascade_coupling", "value": 0.31},
                {"kind": "max_steps", "value": 35},
            ],
        }
    )
    assert len(steps) == 2
    assert steps[0]["kind"] == "cascade_coupling"
    assert steps[1]["value"] == 35


def test_parse_resource_cascade_chain_rejects_bad_schema():
    with pytest.raises(ValueError, match="schema"):
        parse_resource_cascade_chain_spec_payload(
            {"schema": "wrong", "steps": [{"kind": "cascade_coupling", "value": 0.1}]}
        )


def test_apply_resource_cascade_mutation_step_float_and_int():
    w = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=20, cascade_coupling=0.26)
    w2 = apply_resource_cascade_mutation_step(w, {"kind": "cascade_coupling", "value": 0.4})
    assert w2.cascade_coupling == 0.4
    assert w2.max_steps == 20
    w3 = apply_resource_cascade_mutation_step(w2, {"kind": "max_steps", "value": 24})
    assert w3.max_steps == 24


def test_mutation_chain_resource_cascade_empty_raises():
    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=12)
    genome = np.random.default_rng(2).uniform(size=(4, 2))
    with pytest.raises(ValueError, match="non-empty"):
        counterfactual_resource_cascade_mutation_chain_with_rollouts(
            genome, template, steps=[], rollout_seed=1, initial_overload=0.05
        )


def test_counterfactual_resource_cascade_mutation_chain_smoke():
    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=22)
    genome = np.random.default_rng(801).uniform(size=(10, 2))
    steps = [{"kind": "cascade_coupling", "value": 0.55}]
    report, base, var = counterfactual_resource_cascade_mutation_chain_with_rollouts(
        genome,
        template,
        steps=steps,
        rollout_seed=9901,
        initial_overload=0.07,
    )
    assert report["intervention"] == "resource_cascade_mutation_chain"
    assert len(report["mutation_steps"]) == 1
    assert base.simulation_mode == "resource_cascade"
    assert var.simulation_mode == "resource_cascade"


def test_mutation_chain_path_trace_resource_cascade_shape():
    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=18)
    genome = np.random.default_rng(802).uniform(size=(8, 2))
    steps = [
        {"kind": "rumor_gain", "value": 0.25},
        {"kind": "overload_decay", "value": 0.9},
    ]
    path = mutation_chain_path_rollouts_resource_cascade(
        genome,
        template,
        steps=steps,
        rollout_seed=9902,
        initial_overload=0.06,
        variant_initial_overload=0.11,
    )
    trace = mutation_chain_path_to_trace_resource_cascade(
        path,
        steps,
        rollout_seed=9902,
        baseline_initial_overload=0.06,
        variant_initial_overload=0.11,
    )
    assert trace["schema"] == CHAIN_PATH_TRACE_RESOURCE_CASCADE_SCHEMA
    assert len(trace["nodes"]) == len(steps) + 1
    assert len(trace["edges"]) == len(steps)
    assert trace["nodes"][-1]["reset_initial_overload"] == pytest.approx(0.11)
