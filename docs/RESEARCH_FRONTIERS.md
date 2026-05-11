# Research frontiers (not shipped as product claims)

This document separates **charter gates** from **aspirational research** so the public repo stays honest about what is frozen vs exploratory.

## Third reference domain (beyond `ResourceCascadeWorld`)

**Shipped second domain:** `ResourceCascadeWorld` + full replay / GA / co-evolution / counterfactual / benchmark bundle parity — see [`phase_j_resource_cascade.md`](phase_j_resource_cascade.md) and [`WHY_RESOURCE_CASCADE.md`](WHY_RESOURCE_CASCADE.md).

**Rule in `BOUNDARIES.md`:** at most **one** new reference domain “in flight” at a time; the stablecoin aggregate + network stack remains the **CI oracle** for encoding and replay contracts.

**Candidates** (not implemented here): alternate liability / infrastructure cascades with different agent surfaces — each would need its own Phase-J-style gate (world module, `RolloutResult`, replay compatibility table, golden bundle, docs).

## Coupled “mega-institution” dynamics

**Non-goal for this repository:** a single coupled state graph where aggregate peg, network contagion, and resource layers exchange mass or liquidity inside one `step()` — that is a different research product than **decoupled** audit composites (`fragility-institutional-composite-v1` / **v2**).

If you pursue coupling, treat it as a **fork**: new world module, new replay schema bump, new benchmarks — do not silently overload the decoupled composite JSON as if it were coupled physics.

## Where tooling already helps

- **Pareto archives** (`pareto-front-v1`) and search exports can be analyzed with **2-D minimization hypervolume** — `fragility_engine.benchmarks.hypervolume.hypervolume_2d_min` (reference point must strictly dominate the front).
- **Mechanical explanation DAG** (`explanation-dag-v1`) — `fragility_engine.explain.explanation_dag` and `scripts/export_explanation_dag.py` — edges are labeled from minimization reports or counterfactual bundles, not from LLM prose.

See also [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) and [`HOW_TO_USE.md`](HOW_TO_USE.md).
