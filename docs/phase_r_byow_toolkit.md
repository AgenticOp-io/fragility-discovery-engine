# Phase R — BYOW toolkit surface

**Status:** proposed (not yet shipped)  
**Normative gates:** [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase R)  
**Depends on:** Phase Q admission optional but recommended (positioning); `docs/BRING_YOUR_OWN_WORLD.md` + `examples/bring_your_own_world.py` already exist as tutorial seed

## Purpose

Make **bring-your-own-world** the primary product surface: installable package, first-class CLI, typed adapter contract, and at least one **generic** worked external example (not a seventh charter domain). The six in-tree toys remain regression oracles; real value is “wire a steppable world → search → minimize → replay evidence.”

## Admission

1. Tutorial seed exists (`docs/BRING_YOUR_OWN_WORLD.md`, `examples/bring_your_own_world.py`).
2. Tracking issue per exit criterion with one named acceptance test.
3. Custom shock vocabulary design note approved before expanding beyond `reserve_loss` / `rumor` (or explicitly defer vocab extension to a follow-up PR under R).

## In scope

### R.1 — Install & CLI

- `pip install` path that works from GitHub Releases / optional PyPI without tribal knowledge.
- `console_scripts` entry points, e.g.:
  - `fragility search` — GA/MC over a registered rollout
  - `fragility minimize` — greedy schedule minimization
  - `fragility replay` — export / validate replay JSON
  - `fragility certify` — thin wrapper around certificate export
- Help text points to BYOW doc, not only toy demos.

### R.2 — Adapter SDK

- Documented, typed `WorldProtocol` + recommended `rollout_fn` template (may live under `fragility_engine.byow` or stay as documented pattern — prefer a small public module).
- Determinism checklist as a pytest helper or CLI `fragility check-world`.
- Example remains **outside** `src/fragility_engine/world/` (no charter domain).

### R.3 — Shock vocabulary (optional within R, gated)

- Either: keep fixed kinds and document mapping tables for adopters, **or**
- Add a thin extension point for custom kind labels with cost weights — behind tests and a schema note. Do not break existing frozen bundles.

### R.4 — Worked generic example

- One additional tutorial world in `examples/` (e.g. simple queue / token-bucket / lease pool) — **generic ops analogy only**, no customer-specific physics.
- End-to-end: search → minimize → replay JSON → open in replay viewer preset or documented local path.

### R.5 — CI hygiene for toolkit

- CI runs on push/PR for core tests (or document why `workflow_dispatch` remains) — at least one automated path that a new contributor can trust.
- CLI smoke tests for new entry points.

## Out of scope

- Seventh reference domain in `world/` + frozen suite row (requires separate charter phase).
- Snapshot/predicate falsification (Phase S).
- Hosted multi-tenant search API / SaaS.
- Calibrating toy domains to look “more real.”
- True multi-objective evolution (NSGA-II etc.) — optional stretch after R.1–R.4; if added, two-objective discipline in `BOUNDARIES.md` still applies.

## Exit criteria

- [ ] Package exposes `console_scripts` (or equivalent) documented in README + `docs/HOW_TO_USE.md`.
- [ ] `fragility search` / `minimize` / `replay` (names may vary) work on `examples/bring_your_own_world.py` without importing private script helpers.
- [ ] Public BYOW module or frozen API surface listed in `docs/REFERENCE.md`.
- [ ] Second generic `examples/` world + short cookbook section in `BRING_YOUR_OWN_WORLD.md`.
- [ ] Pytest coverage for CLI entry points + determinism helper.
- [ ] README leads with BYOW install → one-day worth-it test → toy domains as oracles.
- [ ] Existing seven frozen bundles still pass `run_benchmark_suite.py --validate`.

## Definition of done for PRs under Phase R

- Prefer vertical slices: CLI first, then SDK module, then second example.
- No changes to golden metrics unless a charter revision is explicit.
- Shock-vocab changes require a migration note and tests that old genomes still decode.
