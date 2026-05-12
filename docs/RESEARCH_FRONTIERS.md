# Research frontiers (not shipped as product claims)

This document separates **charter gates** from **aspirational research** so the public repo stays honest about what is frozen vs exploratory.

## Shipped thin-domain kernels (resource cascade, service backlog)

**Shipped second domain:** `ResourceCascadeWorld` + full replay / GA / co-evolution / counterfactual / benchmark bundle parity — see [`phase_j_resource_cascade.md`](phase_j_resource_cascade.md) and [`WHY_RESOURCE_CASCADE.md`](WHY_RESOURCE_CASCADE.md).

**Third domain (Phase M):** **`ServiceBacklogWorld`** is **shipped** (`simulation_mode` **`service_backlog`**, bundle **`service_backlog_rollout_v1`**). Narrative: [`WHY_SERVICE_BACKLOG.md`](WHY_SERVICE_BACKLOG.md). Gate + replay table: **[`docs/phase_m_third_reference_domain.md`](phase_m_third_reference_domain.md)**; status: [`BOUNDARIES.md`](../BOUNDARIES.md) **Phase M**.

## Coupled “mega-institution” dynamics

**Non-goal for this repository:** a single coupled state graph where aggregate peg, network contagion, and resource layers exchange mass or liquidity inside one `step()` — that is a different research product than **decoupled** audit composites (`fragility-institutional-composite-v1` / **v2** / **v3**).

If you pursue coupling, treat it as a **fork**: new world module, new replay schema bump, new benchmarks — do not silently overload the decoupled composite JSON as if it were coupled physics.

## Where tooling already helps

- **Pareto archives** (`pareto-front-v1`) and search exports can be analyzed with **2-D minimization hypervolume** — `fragility_engine.benchmarks.hypervolume.hypervolume_2d_min` (reference point must strictly dominate the front).
- **Mechanical explanation DAG** (`explanation-dag-v1`) — `fragility_engine.explain.explanation_dag` and `scripts/export_explanation_dag.py` — edges are labeled from minimization reports or counterfactual bundles, not from LLM prose.

See also [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md), [`HOW_TO_USE.md`](HOW_TO_USE.md), and **[`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md)** (policy for coupled multi-kernel work outside this repo).
