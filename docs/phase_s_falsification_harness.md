# Phase S — Falsification harness

**Status:** **shipped** (v0.6.0)  
**Normative gates:** [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase S)  
**Depends on:** Phase R.1–R.2 (CLI + adapter surface) — do not start S until a custom world can be searched via the public toolkit path

## Purpose

Generalize the engine beyond dynamical “physics” sims into a **falsification / red-team harness**: adversarial search over perturbation sequences against any system that can **reset**, **step**, and report **damage as a predicate** (invariant violated), with a reproducible replay of the failing sequence.

This is chaos-engineering / property-based testing for resettable systems — not a seventh toy domain and not coupled institution modeling.

## Admission

1. Phase R exit criteria for CLI + BYOW adapter SDK are checked (or explicitly waived in writing with a thinner S.0 spike).
2. Design note: reset cost model + max rollouts budget (search does thousands of resets).
3. Tracking issue per exit criterion; one acceptance test named up front.
4. No proprietary third-party system details in-tree — examples stay generic.

## In scope

### S.1 — Predicate damage contract

- Document and implement a pattern where `is_collapsed()` (or a parallel `claim_violated()`) is a **boolean invariant**, and `instability_score()` may be a distance-to-violation heuristic (or constant).
- Schema note: `simulation_mode` / meta field distinguishing `dynamics_v1` vs `falsification_v1` rollouts.
- FEL: optional registry entry for falsification evidence constructors (naming only; no parser required).

### S.2 — Snapshot reset adapter interface

- Protocol or base helper: `reset()` restores a named snapshot id; `step(events)` applies one parameterized operation.
- In-memory / filesystem snapshot example only (e.g. tempdir state machine, SQLite file copy) — keep dependencies light.
- Document reset-cost warning in `SCALE_AND_LIMITS.md`.

### S.3 — Minimal failing sequence as bug report

- Reuse greedy minimization → export replay JSON whose trajectory is the **shortest kept shock sequence** that still violates the claim.
- Optional: one-page “how to file this replay as a regression fixture” in docs.

### S.4 — Generic worked example

- In-tree example under `examples/falsification_*` — e.g. a tiny key-value store or queue with an explicit invariant (“stale never outranks fresh”, “denied rate below threshold”, “capacity never negative after reclaim”).
- Search finds a non-obvious ordering that breaks the claim; minimization shrinks it; replay reloads.

## Out of scope

- Hosting customer production systems or ingesting proprietary corpora.
- Claiming absence of bugs (search finds presence of failures only).
- Pearl-grade causal identification.
- Coupled mega-models on `main`.
- LLM agents choosing steps inside the harness loop.
- Turning Phase S into a SaaS red-team product in this phase.

## Exit criteria

- [x] Documented falsification contract in `docs/BRING_YOUR_OWN_WORLD.md` (or `docs/FALSIFICATION_HARNESS.md`) with reset/step/predicate table.
- [x] Reference adapter module (e.g. `fragility_engine.falsify` or `examples/`-only helpers) + tests for determinism under snapshot restore.
- [x] At least one `examples/falsification_*.py` that: searches → collapses on predicate → minimizes → writes replay JSON.
- [x] Replay `meta` marks falsification mode; viewer still loads trajectory (even if physics-specific panels are empty).
- [x] `SCALE_AND_LIMITS.md` states reset-cost and “presence not absence” limits.
- [x] Frozen charter bundles unaffected (no golden metric drift).

## Definition of done for PRs under Phase S

- Examples must be generic and self-contained.
- Prefer presence-of-failure demos with pinned seeds over large stochastic suites.
- Any new schema string gets a row in FEL `SCHEMA_REGISTRY` or an explicit “informative only” note.
