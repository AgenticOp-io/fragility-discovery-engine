# Coupled “mega-institution” dynamics — fork policy

This repository ships **decoupled** reference kernels (aggregate peg, network contagion, resource cascade, service backlog) and **audit composites** that evaluate the **same shock schedule** on multiple kernels **without** shared mutable state across `World.step()`.

## Why not here

A **single coupled state graph** (liquidity, overload, backlog, and network panic exchanging mass or signals inside one `step()`) is a **different research product**: new physics contracts, replay schema decisions, benchmark oracles, and attribution semantics. Shipping it inside this repo would blur the charter in [`BOUNDARIES.md`](../BOUNDARIES.md) and the non-goals in [`RESEARCH_FRONTIERS.md`](RESEARCH_FRONTIERS.md).

## If you pursue it

Treat as a **fork** (or a clearly named sibling package):

1. New `World` (or orchestrator) module with an explicit coupling contract.
2. **Schema bump** for replay JSON (or a new top-level artifact) with migration notes and viewer guidance.
3. New **Phase H–style** golden bundles; do **not** overload `fragility-institutional-composite-v*` JSON as if it were coupled physics.
4. Link back to this engine for **schedule encoding**, **search**, and **counterfactual** patterns where reuse is honest.

## Related shipped tooling

Use **institutional composite v1–v3** only for **side-by-side** metrics under identical schedules (`scripts/institutional_composite_demo.py`).
