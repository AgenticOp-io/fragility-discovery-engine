"""Service-backlog cumulative mutation chains (Phase M / J-style parity)."""

from __future__ import annotations

import numpy as np
import pytest

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual_chain_service_backlog import (
    SERVICE_BACKLOG_CHAIN_SPEC_SCHEMA,
    apply_service_backlog_mutation_step,
    counterfactual_service_backlog_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts_service_backlog,
    parse_service_backlog_chain_spec_payload,
)
from fragility_engine.explain.trace import (
    CHAIN_PATH_TRACE_SERVICE_BACKLOG_SCHEMA,
    mutation_chain_path_to_trace_service_backlog,
)
from fragility_engine.world.service_backlog import ServiceBacklogWorld


def test_parse_service_backlog_chain_spec_smoke():
    steps = parse_service_backlog_chain_spec_payload(
        {
            "schema": SERVICE_BACKLOG_CHAIN_SPEC_SCHEMA,
            "steps": [
                {"kind": "process_rate", "value": 0.41},
                {"kind": "max_steps", "value": 35},
            ],
        }
    )
    assert len(steps) == 2
    assert steps[0]["kind"] == "process_rate"
    assert steps[1]["value"] == 35


def test_parse_service_backlog_chain_rejects_bad_schema():
    with pytest.raises(ValueError, match="schema"):
        parse_service_backlog_chain_spec_payload(
            {"schema": "wrong", "steps": [{"kind": "process_rate", "value": 0.1}]}
        )


def test_apply_service_backlog_mutation_step_float_and_int():
    w = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=20, process_rate=0.26)
    w2 = apply_service_backlog_mutation_step(w, {"kind": "process_rate", "value": 0.4})
    assert w2.process_rate == 0.4
    assert w2.max_steps == 20
    w3 = apply_service_backlog_mutation_step(w2, {"kind": "max_steps", "value": 24})
    assert w3.max_steps == 24


def test_mutation_chain_service_backlog_empty_raises():
    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=12)
    genome = np.random.default_rng(2).uniform(size=(4, 2))
    with pytest.raises(ValueError, match="non-empty"):
        counterfactual_service_backlog_mutation_chain_with_rollouts(
            genome, template, steps=[], rollout_seed=1, initial_backlog=0.05
        )


def test_counterfactual_service_backlog_mutation_chain_smoke():
    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=22)
    genome = np.random.default_rng(801).uniform(size=(10, 2))
    steps = [{"kind": "ingest_gain", "value": 0.55}]
    report, base, var = counterfactual_service_backlog_mutation_chain_with_rollouts(
        genome,
        template,
        steps=steps,
        rollout_seed=9901,
        initial_backlog=0.07,
    )
    assert report["intervention"] == "service_backlog_mutation_chain"
    assert len(report["mutation_steps"]) == 1
    assert base.simulation_mode == "service_backlog"
    assert var.simulation_mode == "service_backlog"


def test_mutation_chain_path_trace_service_backlog_shape():
    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=18)
    genome = np.random.default_rng(802).uniform(size=(8, 2))
    steps = [
        {"kind": "rumor_slack_damage", "value": 0.25},
        {"kind": "slack_recovery", "value": 0.9},
    ]
    path = mutation_chain_path_rollouts_service_backlog(
        genome,
        template,
        steps=steps,
        rollout_seed=9902,
        initial_backlog=0.06,
        variant_initial_backlog=0.11,
    )
    trace = mutation_chain_path_to_trace_service_backlog(
        path,
        steps,
        rollout_seed=9902,
        baseline_initial_backlog=0.06,
        variant_initial_backlog=0.11,
    )
    assert trace["schema"] == CHAIN_PATH_TRACE_SERVICE_BACKLOG_SCHEMA
    assert len(trace["nodes"]) == len(steps) + 1
    assert len(trace["edges"]) == len(steps)
    assert trace["nodes"][-1]["reset_initial_backlog"] == pytest.approx(0.11)
