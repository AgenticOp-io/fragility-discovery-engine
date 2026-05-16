# Bundled artifacts (checked in for demos and CI)

Frozen JSON under `artifacts/` supports static viewers and regression pins without re-running search. Regenerate everything:

```bash
python scripts/regenerate_bundled_viewer_samples.py
```

## Replay viewer (`artifacts/replay_viewer/`)

| File | Source |
|------|--------|
| `sample_replay.json` | `aggregate_rollout_v1` bundle |
| `sample_network_replay.json` | `network_er_rollout_v1` |
| `sample_resource_cascade_replay.json` | `resource_cascade_rollout_v1` |
| `sample_service_backlog_replay.json` | `service_backlog_rollout_v1` |

## Pareto viewer (`artifacts/pareto_viewer/`)

| File | Source |
|------|--------|
| `sample_pareto_front.json` | `export_pareto_front.py --mode aggregate` (short GA) |
| `sample_pareto_resource_cascade.json` | `--mode resource_cascade` |
| `sample_pareto_service_backlog.json` | `--mode service_backlog` |

Preset also links `../flagship/bundled/pareto_front.json` (see flagship section).

## Attribution viewer (`artifacts/attribution_viewer/`)

| File | Source |
|------|--------|
| `sample_attribution_merge_resource_cascade.json` | `export_resource_cascade_joint_attribution.py` |
| `sample_attribution_merge_resource_cascade_triple.json` | `export_resource_cascade_triple_attribution.py` |
| `sample_triple_interaction_summary.json` | `summarize_attribution_merge` on triple merge |
| `sample_network_chain_contagion_base_panic.json` | `export_counterfactual_chain.py` + fixture |
| `sample_aggregate_chain_rumor_depeg.json` | `export_aggregate_counterfactual_chain.py` |
| `sample_resource_cascade_chain_coupling_rumor.json` | `export_resource_cascade_counterfactual_chain.py` |
| `sample_service_backlog_chain_process_ingest.json` | `export_service_backlog_counterfactual_chain.py` |

## Composite demo + viewer

| File | Schema |
|------|--------|
| `composite_demo/sample_twin_composite.json` | v1 (network + resource_cascade) |
| `composite_demo/sample_triple_composite.json` | v2 (+ aggregate) |
| `composite_demo/sample_quad_composite.json` | v3 (+ service_backlog) |

Open `artifacts/composite_viewer/index.html` over HTTP for presets.

## Flagship bundled (`artifacts/flagship/bundled/`)

Short GA run: `best_replay.json`, `pareto_front.json`, `fragility_certificate.json`. CI validates via `scripts/check_flagship_bundled.py`.

## CI pins (benchmark layer)

| Script | Pins |
|--------|------|
| `check_manifest_digest.py` | `GOLDEN_METRICS` digest |
| `check_manifest_inventory.py` | bundle ids + integral bands + digest |
| `check_manifest_summary.py` | log-friendly manifest summary text |
| `validate_viewer_presets.py` | bundled viewer preset paths exist |
