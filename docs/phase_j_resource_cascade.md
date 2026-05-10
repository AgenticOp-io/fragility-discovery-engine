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

## Counterfactuals (thin slice)

- **`remove_steps`:** same semantics as aggregate/network — zero selected shock rows; evaluator pins **`initial_overload`** via CLI (`export_counterfactual.py --mode resource_cascade --initial-overload …`).
- **`initial_overload_shift`:** same genome + rollout seed; variant changes **`--variant-initial-overload`** (`counterfactual_resource_cascade_initial_overload_shift_with_rollouts`).
- **`cascade_coupling_shift`:** same genome, seed, and **`initial_overload`**; variant template clone with **`--variant-cascade-coupling`** (`counterfactual_resource_cascade_cascade_coupling_shift_with_rollouts`).
- **Joint star-merge:** `scripts/export_resource_cascade_joint_attribution.py` merges **remove_steps** + **`--second-branch`** **initial_overload_shift** or **cascade_coupling_shift** (`attribution-merge-v1` → `artifacts/attribution_viewer/index.html`).
- **Scalar ε-sweep:** `counterfactual_epsilon_sweep.py --mode resource_cascade --axis initial_overload --values …` (+ optional `--emit-trace` → `explanation-trace-v1`).

## Mutation chains (cumulative physics)

- **Spec:** `resource-cascade-mutation-chain-spec-v1` — JSON `steps` with `kind` in `{cascade_coupling, overload_decay, rumor_gain, reserve_hit_primary, reserve_hit_secondary, redeem_damage_primary, collapse_headroom, recovery_headroom, max_steps}` and scalar `value`.
- **API:** `fragility_engine.explain.counterfactual_chain_resource_cascade` (`counterfactual_resource_cascade_mutation_chain_with_rollouts`, `mutation_chain_path_rollouts_resource_cascade`).
- **Path trace schema:** `explanation-mutation-chain-path-resource-cascade-v1` via `mutation_chain_path_to_trace_resource_cascade`.
- **CLI:** `scripts/export_resource_cascade_counterfactual_chain.py --chain-json …`.
- **Viewer:** `artifacts/attribution_viewer/index.html` loads path traces with **`reset_initial_overload`** labels (same UI entry point as network chain paths).

## Limits / non-goals

- Not calibrated to any real infrastructure dataset.
