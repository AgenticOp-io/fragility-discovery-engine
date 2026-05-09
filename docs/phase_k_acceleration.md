# Phase K — acceleration scaffold (design notes)

Phase K is defined at a high level in [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) (*honest performance & optional accelerated backends*). This document records **hook points** and **non-goals** so experiments do not fork semantics silently.

## Goals

- Preserve **bitwise determinism per seed** for the NumPy reference path (current default).
- Allow **optional** faster backends only behind explicit configuration, with **golden parity** against existing bundles (especially Phase H `*_rollout_v1` IDs in `fragility_engine.benchmarks.suite`).
- Document **batch / parallel evaluation** ordering if independent rollouts are evaluated concurrently (same seed ⇒ same result regardless of scheduling only when each rollout is isolated).

## Non-goals

- Replacing the thin world/adversary boundary with fused kernels that hide shocks or defenses.
- Implicit nondeterminism (e.g. race-sensitive reductions without a stated ordering contract).
- Mandatory dependency on GPU or proprietary runtimes.

## Suggested integration hooks

| Layer | Hook | Notes |
|-------|------|--------|
| Worlds | `World.step` / internal state update | Swap NumPy-only math for Numba/JAX/etc. only if state transitions match reference tests. |
| Runner | `rollout_*` loops | Optional batched evaluation of **independent** `(genome, seed)` pairs; document reduction order if vectorized. |
| Search | `genetic_search` / co-evolution | Parallel fitness evaluation must not mutate shared RNG state across workers. |

## Optional environment flag pattern

Libraries often use an explicit toggle (examples: `FRAGILITY_BACKEND=numpy|numba`, `JAX_PLATFORM_NAME=cpu`). Any adoption here should:

1. Default to **NumPy** when unset.
2. Be mentioned in [`BOUNDARIES.md`](../BOUNDARIES.md) when behavior or tolerances change.
3. Keep **`pytest`** green on the default path in CI.

## Exit criteria (reminder)

Promote Phase K in `BOUNDARIES.md` only when named bundles show documented speedups **and** CI remains on the reference path with frozen goldens (or documented relaxed tolerances per bundle ID).
