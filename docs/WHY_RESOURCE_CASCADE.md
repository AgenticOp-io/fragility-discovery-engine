# Why `ResourceCascadeWorld`? (Phase J — ≤ 1 page)

## Problem this domain solves

The stablecoin kernel is the **regression oracle**: it must stay frozen enough that CI meaningfully guards regressions. That same constraint makes it a **weak proof of architecture transfer** — reviewers can always say *“cool toy, but the stack only fits one cartoon.”*

**`ResourceCascadeWorld`** is a deliberately small second world that reuses the **same adversary surface** (shock schedules from the same genome encoding, same `attack_cost`, same replay envelope) while changing **only** the physics story: two coupled capacity layers plus an overload state, without peg arithmetic or graph contagion.

If search, replay export, benchmarks, and GA demos run **without forking** the encoding layer, the **engine** (not the domain wallpaper) is what generalizes.

## What we claim — and do not claim

**In scope**

- Deterministic rollouts and replay JSON compatible with `schema_version` **0.4.0** (see [`phase_j_resource_cascade.md`](phase_j_resource_cascade.md)).
- Same schedule → same JSON shape of shocks in `events_lane`; physics maps shocks into different state dynamics.
- Phase **H** golden bundle `resource_cascade_rollout_v1` pins scalar outcomes next to stablecoin bundles.

**Out of scope**

- Any calibration to real operators, OT networks, or empirical cascades.
- Phase I-style counterfactual / merge tooling on this domain until explicitly gated (defender genome + co-evolution/Pareto CLIs are mirrored from aggregate/network).
- “Because two worlds exist, identification is causal” — **no**. Counterfactuals remain scenario labeling, not Pearl-ID.

## How to try it

- One-shot rollout tests: `tests/test_resource_cascade_rollout.py`, `tests/test_replay_contract_resource_cascade.py`.
- GA + minimization demo: `python scripts/run_resource_cascade_ga_demo.py --export-replay artifacts/tmp_rc.json`
- Plain replay export: `python scripts/export_replay.py --mode resource_cascade --out artifacts/tmp_rc_rep.json`
- Counterfactuals: `scripts/export_counterfactual.py --mode resource_cascade` (`remove_steps`, `initial_overload_shift`); joint merge `scripts/export_resource_cascade_joint_attribution.py`; ε-sweep `counterfactual_epsilon_sweep.py --mode resource_cascade --axis initial_overload`.
- Co-evolution / Pareto: `scripts/run_coevolution.py` / `scripts/export_pareto_front.py` with `--mode resource_cascade`.
- Benchmark row: `python scripts/run_benchmark_suite.py --validate` (includes `resource_cascade_rollout_v1`).

## Relationship to the stablecoin reference

Stablecoin aggregate/network worlds remain the **primary** narrative and the **stricter** integration surface (co-evolution, Pareto tooling, counterfactual grammar). Resource cascade is **additive evidence** that the seam between `adversary` / `runner` / `world` is not peg-specific — not a replacement domain.
