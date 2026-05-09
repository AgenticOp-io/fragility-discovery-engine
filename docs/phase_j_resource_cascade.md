# Phase J scaffold — `ResourceCascadeWorld`

**Narrative (“why this domain”):** [`WHY_RESOURCE_CASCADE.md`](WHY_RESOURCE_CASCADE.md).

This domain is a **deliberately thin** second reference: same attacker schedule decoding (`decode_schedule`, `schedule_attack_cost`) as the stablecoin worlds, but physics is a **two-layer capacity cascade** with an overload state — no peg, no reserves/supply accounting.

## Why this exists

- Proves the **engine wiring** (world module + `RolloutResult` + replay JSON) generalizes without forking the adversary encoding.
- Keeps **stablecoin bundles** as the numeric CI oracle (`tests/test_benchmark_suite.py`, etc.).

## API

- World: `fragility_engine.world.resource_cascade.ResourceCascadeWorld`
- Rollout: `fragility_engine.runner.rollout_resource_cascade`
- Replay: `rollout_to_replay_dict` — `simulation_mode` is **`resource_cascade`** (`schema_version` unchanged).

## Replay JSON compatibility (schema **0.4.0**)

| Field | Aggregate / network | `resource_cascade` |
|--------|---------------------|-------------------|
| Top-level keys | `schema_version`, `simulation_mode`, costs, collapse, `events_lane`, `trajectory`, recoverability extras | **Same** |
| `simulation_mode` | `aggregate` \| `network` | **`resource_cascade`** |
| `state_vector` layout | domain-specific length | **`[h0, h1, overload, timestep]`** (4 floats) |
| `metrics.price` | peg ratio | **min layer headroom** (still drives viewer blue trace) |
| `metrics.instability` | peg instability | overload + headroom shortfall |

Static **`replay_viewer`** treats unknown modes like aggregate for plotting (price + instability scales).

## Co-evolution, Pareto, defender

- Same **four-slot defender genome** decoding as aggregate/network (`build_defended_resource_cascade_world`): knobs map to `overload_decay`, `rumor_gain`, `recovery_headroom`, and **`reserve_boost`** damps effective initial overload at `reset`.
- **CLI:** `scripts/run_coevolution.py --mode resource_cascade --initial-overload …`; `scripts/export_pareto_front.py --mode resource_cascade`.
- **API:** `fragility_engine.coevolution.alternating_coevolution_resource_cascade`.

## Limits / non-goals

- Not calibrated to any real infrastructure dataset.
- No dedicated counterfactual / attribution vocabulary for this domain yet (stablecoin + network grammars remain the reference for Phase I-style merges).
