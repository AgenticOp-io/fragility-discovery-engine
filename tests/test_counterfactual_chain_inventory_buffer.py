"""Inventory-buffer cumulative mutation chains."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual_chain_inventory_buffer import (
    INVENTORY_BUFFER_CHAIN_SPEC_SCHEMA,
    counterfactual_inventory_buffer_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts_inventory_buffer,
    parse_inventory_buffer_chain_spec_payload,
)
from fragility_engine.explain.trace import (
    CHAIN_PATH_TRACE_INVENTORY_BUFFER_SCHEMA,
    mutation_chain_path_to_trace_inventory_buffer,
)
from fragility_engine.world.inventory_buffer import InventoryBufferWorld

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "chains" / "inventory_buffer_demand_fulfillment_chain.json"
)


def test_parse_inventory_buffer_chain_spec_fixture() -> None:
    steps = parse_inventory_buffer_chain_spec_payload(json.loads(FIXTURE.read_text(encoding="utf-8")))
    assert len(steps) == 2
    assert steps[0]["kind"] == "demand_spike_gain"


def test_counterfactual_inventory_buffer_mutation_chain_smoke() -> None:
    steps = parse_inventory_buffer_chain_spec_payload(json.loads(FIXTURE.read_text(encoding="utf-8")))
    template = InventoryBufferWorld(population=default_stablecoin_population(), max_steps=24)
    genome = np.random.default_rng(11).uniform(size=(10, 2))
    report, base, var = counterfactual_inventory_buffer_mutation_chain_with_rollouts(
        genome,
        template,
        steps=steps,
        rollout_seed=5501,
        initial_stock=0.88,
    )
    assert report["intervention"] == "inventory_buffer_mutation_chain"
    assert len(report["mutation_steps"]) == 2
    assert base.simulation_mode == "inventory_buffer"


def test_mutation_chain_path_trace_inventory_buffer_shape() -> None:
    steps = parse_inventory_buffer_chain_spec_payload(json.loads(FIXTURE.read_text(encoding="utf-8")))
    template = InventoryBufferWorld(population=default_stablecoin_population(), max_steps=22)
    genome = np.random.default_rng(12).uniform(size=(8, 2))
    path = mutation_chain_path_rollouts_inventory_buffer(
        genome,
        template,
        steps=steps,
        rollout_seed=5502,
        initial_stock=0.86,
    )
    trace = mutation_chain_path_to_trace_inventory_buffer(
        path,
        steps,
        rollout_seed=5502,
        baseline_initial_stock=0.86,
        variant_initial_stock=0.86,
    )
    assert trace["schema"] == CHAIN_PATH_TRACE_INVENTORY_BUFFER_SCHEMA
    assert trace["source_chain_schema"] == INVENTORY_BUFFER_CHAIN_SPEC_SCHEMA
    assert len(trace["nodes"]) == len(steps) + 1
