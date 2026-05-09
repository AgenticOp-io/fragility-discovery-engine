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

## Limits / non-goals

- Not calibrated to any real infrastructure dataset.
- No co-evolution / defender hook yet — add only with explicit tests mirroring aggregate/network discipline.
