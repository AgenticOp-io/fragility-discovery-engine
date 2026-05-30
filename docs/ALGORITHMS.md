# Algorithms and provenance

This document lists every algorithm the Fragility Discovery Engine uses, who invented it, and where you can find the implementation in this repository. The engine has **two runtime dependencies** — `numpy` and `networkx` — so everything below is hand-rolled on top of NumPy unless noted.

For the formal evidence vocabulary (schedules, rollouts, Δ⁻/Δ⁺ attribution, schema IDs), see [Fragility Evidence Language (FEL)](FRAGILITY_EVIDENCE_LANGUAGE.md).


| Notation     | Meaning                                                                           |
| ------------ | --------------------------------------------------------------------------------- |
| **Original** | First implementation; framing introduced by this project.                         |
| **Standard** | Textbook algorithm we re-implemented from first principles (no external library). |
| **Library**  | Provided by a third-party package we depend on.                                   |


---

## 1. What we created (named, in one place)

These are the algorithms, frameworks, and physics kernels **originated by this project**. Each is fully documented in the section linked from the table; this is a single index so the contribution is visible at a glance.

**Explanation and attribution methods**


| Name                                       | What it does                                                                                                                                                                                                                                                                                                      | Where to read | Code                                                         |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------ |
| Schedule-mask counterfactual               | Re-run a simulator with selected shock timesteps deterministically zeroed and diff the rollouts to attribute outcome change to those steps. Builds on Pearl's `do`-calculus framing; the schedule-mask + replay-diff pipeline is ours.                                                                            | §3.1          | `src/fragility_engine/explain/counterfactual.py`             |
| Greedy shock-set minimization for collapse | Position-greedy reduction of an attacker schedule to the smallest subset of shocks that still drives the world to collapse, with pinned rollout seeds throughout. Applies the delta-debugging idea (Zeller & Hildebrandt 2002) to adversarial simulation schedules; the specific algorithm is greedy-by-timestep. | §3.2          | `src/fragility_engine/explain/minimal_collapse.py`           |
| Mutation-chain path trace                  | Apply discrete world-physics mutations one at a time in a chosen order; record `Δ integral_instability` and `Δ attack_cost` at every step. Analogous in spirit to integrated gradients / SHAP but defined directly over a discrete simulator.                                                                     | §3.3          | `src/fragility_engine/explain/counterfactual_chain*.py`      |
| Star-merge attribution graph               | Merge several single-branch counterfactual bundles that share one baseline into one graph (root = baseline, leaves = branches, edges carry Δ-metrics and intervention labels), with strict baseline-equality checking. Schema `attribution-merge-v1`.                                                             | §3.4          | `src/fragility_engine/explain/merge_attribution.py`          |
| Fragility Evidence Language (FEL)          | Formal vocabulary for worlds, schedules, rollouts, attack Pareto order, Δ⁻ counterfactual vs Δ⁺ path attribution, and evidence schema IDs — not new physics.                                                                                                                                                      | [FEL](FRAGILITY_EVIDENCE_LANGUAGE.md) | `src/fragility_engine/fel/`                                  |
| Schedule-minimization explanation DAG      | Compact DAG (`explanation-dag-v1`) over a minimization report: `baseline → minimized` with the kept events on the edge. Machine-readable "why did it still collapse?" record.                                                                                                                                     | §3.5          | `src/fragility_engine/explain/explanation_dag.py`            |
| Institutional composite                    | Run the same attacker schedule through several decoupled physics kernels and emit a side-by-side scorecard JSON (`fragility-institutional-composite-v1…v4`). Kernels never exchange state inside a step.                                                                                                          | §4.7          | `src/fragility_engine/benchmarks/institutional_composite.py` |


**Reproducibility framework**


| Name                                   | What it does                                                                                                                                                                                            | Where to read | Code                                                                              |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------- |
| Frozen-benchmark golden-metric harness | Benchmark suite where each bundle pins `(genome_seed, rollout_seed)` and asserts scalar metrics on every CI run. Conceptually similar to MLPerf, but for adversarial search rather than model training. | §5.1          | `src/fragility_engine/benchmarks/suite.py`, `scripts/run_benchmark_suite.py`      |
| Manifest digest pinning                | SHA-256 over the benchmark inventory; CI fails if the digest drifts without an explicit bump. Standard hash, original workflow.                                                                         | §5.2          | `src/fragility_engine/benchmarks/manifest.py`, `scripts/check_manifest_digest.py` |
| Fragility certificate                  | Single JSON that bundles a flagship replay + Pareto front + environment fingerprint into one signed, citeable artifact — paper-appendix or audit attachment. Schema `fragility-certificate-v1`.         | §5.3          | `src/fragility_engine/benchmarks/certificate.py`                                  |


**Physics kernels** (deliberately simplified; not calibrated to any real institution)


| Name                              | What it does                                                                                                                                     | Where to read | Code                                             |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------- | ------------------------------------------------ |
| Aggregate peg kernel              | Scalar reserves/supply with panic + redemption coupling.                                                                                         | §4.1          | `src/fragility_engine/world/stablecoin_peg.py`   |
| Two-layer resource-cascade kernel | Coupled headrooms `(h₀, h₁)` with a shared overload state; reduces a Motter–Lai cascade to its smallest still-interesting form.                  | §4.3          | `src/fragility_engine/world/resource_cascade.py` |
| Service-backlog kernel            | Backlog grows with demand, shrinks with process rate; collapse on sustained over-threshold backlog.                                              | §4.4          | `src/fragility_engine/world/service_backlog.py`  |
| Liquidity-ladder kernel           | Margin utilization vs funding-ladder depth with deleveraging on haircut breach; reproduces the margin-call spiral mechanic in 4 state variables. | §4.5          | `src/fragility_engine/world/liquidity_ladder.py` |
| Inventory-buffer kernel           | Stock level under demand spikes and fulfillment erosion; sixth reference domain shipped in v0.5.                                                 | §4.6          | `src/fragility_engine/world/inventory_buffer.py` |


All kernels share **one schedule encoding** (`src/fragility_engine/adversary/encoding.py`), so any attack found by search transfers across kernels unchanged — itself an intentional design choice of this project.

Everything else listed in §2–§6 is textbook or library; we cite the original sources for those below.

---

## 2. Adversary search

### 2.1 Monte Carlo random search — Standard

Draws `samples` random genomes, evaluates fitness, keeps the best.

- **Originators:** Common baseline; Metropolis & Ulam coined "Monte Carlo" in 1949 ([von Neumann & Ulam, 1947](https://library.lanl.gov/cgi-bin/getfile?00326866.pdf)). The "uniform random search" baseline is canonical (e.g. Bergstra & Bengio 2012, *[Random Search for Hyper-Parameter Optimization](https://www.jmlr.org/papers/v13/bergstra12a.html)*).
- **Our code:** `src/fragility_engine/adversary/search.py::monte_carlo_search`
- **Notes:** Used as the reference baseline against which the GA's improvement is measured.

### 2.2 Genetic algorithm (real-valued) — Standard

Population of real-valued genomes, elitist selection, single-point crossover, Gaussian mutation with per-gene mask.

- **Originators:** Holland (1975), *Adaptation in Natural and Artificial Systems*; Goldberg (1989), *Genetic Algorithms in Search, Optimization and Machine Learning*. Real-valued ("evolution strategies") variant: Rechenberg (1971), Schwefel (1977). Gaussian mutation: Schwefel (1965).
- **Our code:**
  - Genome encoding: `adversary/encoding.py` (shape `(horizon, 2)` ∈ `[0,1]²`, decoded to `(shock_kind, magnitude)` per timestep).
  - Operators: `mutate_genome`, `crossover_genome` in `encoding.py`.
  - Search loop: `adversary/search.py::genetic_search` (and `genetic_vector_search` for defender genomes).
- **Why we re-implemented:** Avoids a heavyweight dependency (DEAP / pymoo) for a 200-line loop, and keeps determinism under our explicit RNG / seed contract.

### 2.3 Pareto archive (2-objective dominance) — Standard

Maintains the non-dominated set across `(severity, attack_cost)`; `severity` maximized, `attack_cost` minimized.

- **Originators:** Vilfredo Pareto (1906), *Manuale di economia politica*. Dominance test as used here: standard formulation in any multi-objective optimization text (e.g. Deb 2001, *Multi-Objective Optimization Using Evolutionary Algorithms*).
- **Our code:** `adversary/pareto.py::pareto_indices` (naive O(N²) pairwise — fine for our archive sizes), `merge_pareto_points`, `rollout_cloud_to_pareto`.
- **Note:** We do **not** use NSGA-II (Deb et al. 2002) — our search isn't multi-objective at fitness time; the archive is a post-hoc projection of the search history.

### 2.4 Two-dimensional hypervolume — Standard

Closed-form rectangular sweep for two minimized objectives relative to a reference point.

- **Originators:** Zitzler & Thiele (1998), *[Multiobjective optimization using evolutionary algorithms — a comparative case study](https://link.springer.com/chapter/10.1007/BFb0056872)* (introduced the "size of the dominated space" indicator). The 2-D O(N log N) sweep is folklore.
- **Our code:** `benchmarks/hypervolume.py::hypervolume_2d_min` (generic minimization) and `hypervolume_2d_attack_pareto` (attack archives via `(-severity, attack_cost)` transform). See [Math reference](MATH.md) §4.
- **Use:** CI regression gate on Pareto-archive quality; never used as a fitness signal.

### 2.5 Alternating attacker / defender co-evolution — Standard

Rounds of (a) attacker GA finds worst schedules against frozen defender, then (b) defender GA finds best parameter vector against frozen attacker; repeat.

- **Originators:** Competitive co-evolution: Hillis (1990), *[Co-evolving parasites improve simulated evolution as an optimization procedure](https://www.sciencedirect.com/science/article/abs/pii/0167278990900762)*. Alternating min-max formulation: classical in adversarial / game-theoretic learning (e.g. Sims 1994 on competitive coevolution; Watson & Pollack 2001 on the "Red Queen" dynamic).
- **Our code:** `coevolution/alternating.py::alternating_coevolution_rollout` plus mode-specific wrappers (`alternating_coevolution_network`, etc.) and `coevolution/thread_safe_template.py` for safe parallel rollouts.
- **Pareto-per-round:** optional `collect_attacker_pareto=True`; archives are merged via `merge_pareto_points`.

---

## 3. Explanation / attribution

### 3.1 Counterfactual remove-steps — Original framing

Re-run the simulation with selected shock timesteps zeroed; compare metrics.

- **Originators:** The general idea — counterfactual evaluation under "do(X = 0)" interventions — comes from Pearl's causal framework ([Pearl 2009](https://bayes.cs.ucla.edu/BOOK-2K/), *Causality*). Our specific formulation (mechanical schedule masking + replay diff) is original to this project.
- **Our code:** `explain/counterfactual.py::counterfactual_remove_steps_with_rollouts`, `compare_rollouts`.
- **Domain variants:** Resource-cascade, service-backlog, liquidity-ladder all expose a `mode` switch on `scripts/export_counterfactual.py`.

### 3.2 Greedy schedule minimization (delta-debugging-style) — Standard idea, original application

Greedy removal of shock timesteps while preserving the `collapsed` outcome — finds the minimal shock set that still breaks the world.

- **Originators:** Algorithmic minimization of inputs while preserving a property: Zeller & Hildebrandt (2002), *[Simplifying and Isolating Failure-Inducing Input](https://www.st.cs.uni-saarland.de/papers/tse2002/)* (delta debugging, ddmin). We use the greedy-by-position variant rather than the divide-and-conquer ddmin variant.
- **Our code:** `explain/minimal_collapse.py::minimize_schedule_with_rollout`.
- **CLI:** `scripts/run_ga_demo.py --export-minimized-replay` and the explicit `scripts/export_minimized_replay.py`.

### 3.3 Mutation-chain path traces — Original

Apply discrete world-physics mutations (e.g. raise `base_panic`, perturb neighbor edges, change capacity) **one at a time** in a chosen order; record `Δ integral_instability` and `Δ attack_cost` at every step.

- **Originators:** The framing (cumulative discrete interventions on a simulator with stepwise contribution accounting) is original to this project. It is analogous in spirit to integrated-gradients ([Sundararajan, Taly & Yan 2017](https://arxiv.org/abs/1703.01365)) and SHAP ([Lundberg & Lee 2017](https://arxiv.org/abs/1705.07874)) but operates on a discrete simulator rather than a differentiable model.
- **Our code:** `explain/counterfactual_chain*.py` (one module per domain), `explain/trace.py`.
- **CLIs:** `scripts/export_counterfactual_chain.py`, `scripts/export_*_counterfactual_chain.py`.

### 3.4 Star-merge attribution — Original

Aggregate several counterfactual bundles that share one baseline into a single graph (baseline → branch₁, baseline → branch₂, …) with Δ-metrics on edges.

- **Originators:** Original to this project.
- **Our code:** `explain/merge_attribution.py::merge_heterogeneous_counterfactuals` (schema `attribution-merge-v1`).
- **CLI:** `scripts/merge_counterfactual_attribution.py`.

### 3.5 Explanation DAG (schedule + minimization) — Original

Tiny DAG over a minimization report: baseline → minimized, with the minimal event set on the edge.

- **Originators:** Original to this project.
- **Our code:** `explain/explanation_dag.py` (schema `explanation-dag-v1`).

---

## 4. Simulation worlds (physics kernels)

All six worlds are **deliberately simplified models**. They are **not calibrated** to any real institution, market, or infrastructure system. Each is original to this project; the underlying mechanisms draw on well-known theory.

### 4.1 Aggregate stablecoin peg — Original kernel

Scalar pool: reserves drain on redemption shocks; panic decays with a fixed time constant; collapse if price < threshold.

- **Mechanism family:** Bank-run models in the Diamond–Dybvig tradition ([Diamond & Dybvig 1983](https://www.journals.uchicago.edu/doi/10.1086/261155)) and "death spiral" stablecoin dynamics analyzed post-Terra (e.g. [Liu, Makarov & Schoar 2023](https://www.nber.org/papers/w31256)).
- **Our code:** `world/stablecoin_peg.py::StablecoinPegWorld`.

### 4.2 Network contagion — Standard diffusion on `networkx` graphs

Per-node panic updates by `pᵢ' ← (1-β) pᵢ + β · mean(pⱼ for j ∈ N(i))`.

- **Mechanism family:** Linear opinion / consensus dynamics — DeGroot (1974), *[Reaching a Consensus](https://www.jstor.org/stable/2285509)*. Threshold contagion: Granovetter (1978), *[Threshold Models of Collective Behavior](https://www.journals.uchicago.edu/doi/abs/10.1086/226707)*, Watts (2002), *[A simple model of global cascades on random networks](https://www.pnas.org/doi/10.1073/pnas.082090499)*. Financial contagion: Eisenberg & Noe (2001) on payment clearing.
- **Topology generators:** Erdős–Rényi (1959) and Watts–Strogatz (1998) — supplied by **networkx** (`erdos_renyi_graph`, `watts_strogatz_graph`).
- **Our code:** `network/contagion.py::contagion_step_lists`, `network/topology.py`, `world/stablecoin_network.py`.

### 4.3 Resource cascade — Original kernel

Two coupled capacity headrooms (`h₀`, `h₁`) with a shared overload state. Overload feeds back into headroom; rumor shocks raise overload; reserve hits drop headroom.

- **Mechanism family:** Cascading failure in capacity systems — Motter & Lai (2002), *[Cascade-based attacks on complex networks](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.66.065102)*. Our two-layer reduction is original.
- **Our code:** `world/resource_cascade.py::ResourceCascadeWorld`. Optional Numba acceleration: `runner_resource_cascade_numba.py` (well-formed parity tested vs. NumPy reference).

### 4.4 Service backlog — Original kernel

Queue length grows with demand, shrinks with process rate; collapse when backlog crosses threshold for too long.

- **Mechanism family:** M/M/1-style queue dynamics ([Kendall 1953](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-24/issue-3/Stochastic-Processes-Occurring-in-the-Theory-of-Queues-and-their/10.1214/aoms/1177728975.full)); operational meltdown ("backlog spiral") informal in ops literature. Specific reduction is original.
- **Our code:** `world/service_backlog.py::ServiceBacklogWorld`.

### 4.5 Liquidity ladder — Original kernel

Margin utilization vs funding-ladder depth; reserve losses and rumor shocks erode runway; deleveraging mechanic when margin breaches haircut thresholds.

- **Mechanism family:** Margin-call spiral / fire-sale literature — Brunnermeier & Pedersen (2009), *[Market Liquidity and Funding Liquidity](https://academic.oup.com/rfs/article/22/6/2201/1592184)*.
- **Our code:** `world/liquidity_ladder.py::LiquidityLadderWorld`.

### 4.6 Inventory buffer — Original kernel

Normalized stock level `S` and fulfillment capacity `F` (both in `[0,1]`). `reserve_loss` shocks drain stock (demand spikes); `rumor` shocks erode fulfillment (supplier / logistics trust). Collapse when stock falls below `stockout_collapse` threshold or fulfillment falls below `fulfillment_floor_collapse`. Distinct from service backlog (queue depth) and peg worlds.

- **Originators:** Original to this project (added in v0.5).
- **Our code:** `src/fragility_engine/world/inventory_buffer.py`, `scripts/run_inventory_buffer_ga_demo.py`.
- **Frozen bundle:** `inventory_buffer_rollout_v1` in `scripts/run_benchmark_suite.py --validate`.

### 4.7 Institutional composite — Original framing

Runs **the same** attacker schedule through several decoupled physics kernels (any subset of aggregate / network / resource_cascade / service_backlog / liquidity_ladder) and emits a side-by-side scorecard JSON. Kernels never exchange state inside a `step()` — this is a multi-kernel audit, not a multi-physics coupling.

- **Originators:** Original to this project. The idea of applying a single stress through multiple decoupled views appears in regulatory stress-testing literature (e.g. EBA / Fed CCAR designs), but as a software primitive over a shared schedule encoding it is ours.
- **Our code:** `benchmarks/institutional_composite.py` (schemas `fragility-institutional-composite-v1` through `v4`).
- **Viewer:** `artifacts/composite_viewer/index.html`.

---

## 5. Benchmark and reproducibility

### 5.1 Frozen-benchmark golden-metric harness — Original framework

Six bundles with pinned `(genome_seed, rollout_seed)` and asserted scalar metrics (within tolerance bands).

- **Originators:** Original to this project (the framework). Conceptually similar to MLPerf-style benchmark suites, but for adversarial search instead of model training.
- **Our code:** `benchmarks/suite.py`, `benchmarks/manifest.py`, `scripts/run_benchmark_suite.py --validate`.

### 5.2 Manifest digest pinning — Standard hash, original workflow

SHA-256 digest of the benchmark inventory; CI fails if digest drifts without an explicit bump.

- **Originators:** SHA-256 — NIST FIPS 180-4. Pinning workflow is original.
- **Our code:** `scripts/check_manifest_digest.py`, `benchmarks/manifest.py`.

### 5.3 Fragility certificate — Original

Bundles a flagship replay + Pareto front + environment fingerprint into a single signed JSON, intended as a paper-appendix or audit attachment.

- **Originators:** Original to this project.
- **Our code:** `benchmarks/certificate.py`, `scripts/export_fragility_certificate.py`.

---

## 6. Third-party libraries (provenance for transitive algorithms)


| Library                                  | Algorithms we rely on                                                                      | Citation                                                                                                                                        |
| ---------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **NumPy**                                | RNG (`PCG64` default), vector ops, linear algebra                                          | [Harris et al., 2020](https://www.nature.com/articles/s41586-020-2649-2), *Nature*. PCG: [O'Neill 2014](https://www.pcg-random.org/paper.html). |
| **networkx**                             | Erdős–Rényi (`gnp_random_graph`), Watts–Strogatz (`watts_strogatz_graph`), graph traversal | [Hagberg, Schult, Swart 2008](https://conference.scipy.org/proceedings/SciPy2008/paper_2/).                                                     |
| **numba** *(optional, accelerate extra)* | JIT compilation of the resource-cascade hot loop                                           | [Lam, Pitrou, Seibert 2015](https://dl.acm.org/doi/10.1145/2833157.2833162).                                                                    |
| **matplotlib** *(optional, viz extra)*   | Static plots in the analysis notebooks                                                     | [Hunter 2007](https://ieeexplore.ieee.org/document/4160265).                                                                                    |


We do **not** use `scipy`, `pymoo`, `DEAP`, `cma`, `optuna`, or any other optimization library — every search, archive, and explanation algorithm above is implemented in this repository.

---

## 7. How to cite this work

If you build on the engine, please cite the project alongside the underlying algorithms above:

```bibtex
@software{fragility_discovery_engine_2026,
  title  = {Fragility Discovery Engine},
  author = {AgenticOp},
  year   = {2026},
  url    = {https://github.com/AgenticOp-io/fragility-discovery-engine},
  version = {v0.5.0}
}
```

---

## 8. Where to read the code


| You want…                             | Start here                                                                                                                |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| The end-to-end rollout loop           | `src/fragility_engine/runner.py`                                                                                          |
| Search loops (MC / GA / Pareto)       | `src/fragility_engine/adversary/search.py`                                                                                |
| Counterfactual primitives             | `src/fragility_engine/explain/counterfactual.py`                                                                          |
| Mutation chains                       | `src/fragility_engine/explain/counterfactual_chain*.py`                                                                   |
| World physics (any domain)            | `src/fragility_engine/world/{stablecoin_peg, stablecoin_network, resource_cascade, service_backlog, liquidity_ladder, inventory_buffer}.py` |
| Benchmark / certificate / hypervolume | `src/fragility_engine/benchmarks/`                                                                                        |
| Frozen JSON schemas (every export)    | `docs/REFERENCE.md` schema index                                                                                          |


