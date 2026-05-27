# Mutation chain fixtures (Phase I)

Small **chain spec** JSON files checked in under `tests/fixtures/chains/`. Use with the matching export CLI and optional `--emit-path-trace`.

| Fixture | Schema | Export CLI |
|---------|--------|------------|
| `aggregate_panic_depeg_chain.json` | `aggregate-mutation-chain-spec-v1` | `scripts/export_aggregate_counterfactual_chain.py` |
| `network_contagion_base_panic_chain.json` | `network-mutation-chain-spec-v1` | `scripts/export_counterfactual_chain.py` (+ `--neighbor-json` for edge steps) |
| `resource_cascade_coupling_rumor_chain.json` | `resource-cascade-mutation-chain-spec-v1` | `scripts/export_resource_cascade_counterfactual_chain.py` |
| `service_backlog_process_ingest_chain.json` | `service-backlog-mutation-chain-spec-v1` | `scripts/export_service_backlog_counterfactual_chain.py` |
| `liquidity_ladder_margin_haircut_chain.json` | `liquidity-ladder-mutation-chain-spec-v1` | `scripts/export_liquidity_ladder_counterfactual_chain.py` |
| `inventory_buffer_demand_fulfillment_chain.json` | `inventory-buffer-mutation-chain-spec-v1` | `scripts/export_inventory_buffer_mutation_chain.py` |

Bundled viewer samples (regenerate): `scripts/regenerate_bundled_viewer_samples.py` → `artifacts/attribution_viewer/sample_*_chain_*.json`.

Cookbooks: [`network_counterfactual_example.md`](network_counterfactual_example.md), [`aggregate_counterfactual_example.md`](aggregate_counterfactual_example.md), [`resource_cascade_counterfactual_example.md`](resource_cascade_counterfactual_example.md), [`service_backlog_counterfactual_example.md`](service_backlog_counterfactual_example.md), [`inventory_buffer_counterfactual_example.md`](inventory_buffer_counterfactual_example.md).
