"""Checked-in demo JSON paths (relative to repository root) for viewers and CI."""

from __future__ import annotations

# Replay viewer
REPLAY_VIEWER_SAMPLES: tuple[str, ...] = (
    "artifacts/replay_viewer/sample_replay.json",
    "artifacts/replay_viewer/sample_network_replay.json",
    "artifacts/replay_viewer/sample_resource_cascade_replay.json",
    "artifacts/replay_viewer/sample_service_backlog_replay.json",
    "artifacts/replay_viewer/sample_liquidity_ladder_replay.json",
    "artifacts/replay_viewer/sample_inventory_buffer_replay.json",
)

# Pareto viewer
PARETO_VIEWER_SAMPLES: tuple[str, ...] = (
    "artifacts/pareto_viewer/sample_pareto_front.json",
    "artifacts/pareto_viewer/sample_pareto_resource_cascade.json",
    "artifacts/pareto_viewer/sample_pareto_service_backlog.json",
    "artifacts/pareto_viewer/sample_pareto_network.json",
    "artifacts/pareto_viewer/sample_pareto_liquidity_ladder.json",
    "artifacts/pareto_viewer/sample_pareto_inventory_buffer.json",
    "artifacts/flagship/bundled/pareto_front.json",
    "artifacts/flagship/bundled/best_replay.json",
    "artifacts/flagship/bundled/fragility_certificate.json",
)

# Attribution viewer
ATTRIBUTION_VIEWER_SAMPLES: tuple[str, ...] = (
    "artifacts/attribution_viewer/sample_attribution_merge_resource_cascade.json",
    "artifacts/attribution_viewer/sample_attribution_merge_resource_cascade_triple.json",
    "artifacts/attribution_viewer/sample_triple_interaction_summary.json",
    "artifacts/attribution_viewer/sample_network_chain_contagion_base_panic.json",
    "artifacts/attribution_viewer/sample_aggregate_chain_rumor_depeg.json",
    "artifacts/attribution_viewer/sample_resource_cascade_chain_coupling_rumor.json",
    "artifacts/attribution_viewer/sample_service_backlog_chain_process_ingest.json",
    "artifacts/attribution_viewer/sample_liquidity_ladder_chain_margin_haircut.json",
    "artifacts/attribution_viewer/sample_inventory_buffer_chain_demand_fulfillment.json",
    "artifacts/attribution_viewer/sample_attribution_merge_inventory_buffer.json",
)

# Composite demo + viewer
COMPOSITE_DEMO_SAMPLES: tuple[str, ...] = (
    "artifacts/composite_demo/sample_twin_composite.json",
    "artifacts/composite_demo/sample_triple_composite.json",
    "artifacts/composite_demo/sample_quad_composite.json",
    "artifacts/composite_demo/sample_penta_composite.json",
    "artifacts/composite_demo/sample_hexa_composite.json",
    "artifacts/attribution_viewer/sample_attribution_merge_liquidity_ladder.json",
    "artifacts/attribution_viewer/sample_attribution_merge_service_backlog.json",
)

# Research fork (coupled_institution) — not charter domains on main
COUPLED_FORK_DEMO: tuple[str, ...] = (
    "artifacts/replay_viewer/sample_coupled_institution_replay.json",
    "artifacts/attribution_viewer/sample_coupled_mutation_chain.json",
    "artifacts/pareto_viewer/sample_pareto_coupled_institution.json",
    "artifacts/coupled_fork_demo/coupling_strength_sweep.json",
    "artifacts/coupled_fork_demo/coupling_strength_sweep.png",
    "artifacts/coupled_fork_demo/sample_coupling_comparison.json",
    "artifacts/coupled_fork_demo/sample_coupled_replay.json",
    "artifacts/coupled_fork_demo/sample_coupled_mutation_chain.json",
    "artifacts/coupled_fork_demo/sample_coupled_pareto_front.json",
)

CHAIN_FIXTURES: tuple[str, ...] = (
    "tests/fixtures/chains/aggregate_panic_depeg_chain.json",
    "tests/fixtures/chains/network_contagion_base_panic_chain.json",
    "tests/fixtures/chains/resource_cascade_coupling_rumor_chain.json",
    "tests/fixtures/chains/service_backlog_process_ingest_chain.json",
    "tests/fixtures/chains/liquidity_ladder_margin_haircut_chain.json",
    "tests/fixtures/chains/inventory_buffer_demand_fulfillment_chain.json",
)

BUNDLED_ARTIFACT_PATHS: tuple[str, ...] = (
    *REPLAY_VIEWER_SAMPLES,
    *PARETO_VIEWER_SAMPLES,
    *ATTRIBUTION_VIEWER_SAMPLES,
    *COMPOSITE_DEMO_SAMPLES,
    *COUPLED_FORK_DEMO,
)
