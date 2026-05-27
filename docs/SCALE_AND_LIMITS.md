# Scale, complexity, and determinism (honest limits)

This document states **what scales how** and **what breaks reproducibility** if misused. It complements `[phase_k_acceleration.md](phase_k_acceleration.md)` (optional backends + threading/process pools).

## Determinism

- **Same seed, same code path, same NumPy reference rollout** ⇒ same trajectory (modulo documented FP tolerances on some bundles).
- **Parallel evaluation** (`eval_workers > 1`) is deterministic **only** when each task owns isolated mutable state (see `coevolution.thread_safe_template` and clone helpers). Sharing one `AgentPopulation` across threads races.
- `**eval_pool="processes"`** requires a **picklable** `rollout_fn` (e.g. `functools.partial(rollout_bundle_with_genome, bundle_id, isolate=True)`). Arbitrary closures from demo scripts will fail pickle on Windows spawn.

## Asymptotics (per timestep mental model)


| Piece                                           | Dominant cost                                                               | Notes                                                                                 |
| ----------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `StablecoinNetworkWorld` step (dense adjacency) | O(n²) mixing in worst case; **neighbor-list** path is **O(edges)** per step | Prefer list topology for large n.                                                     |
| `StablecoinPegWorld`                            | O(archetypes)                                                               | Aggregate reference.                                                                  |
| `ResourceCascadeWorld`                          | O(archetypes); optional Numba path                                          | See `FRAGILITY_RESOURCE_CASCADE_BACKEND`.                                             |
| `ServiceBacklogWorld`                           | O(archetypes); NumPy rollout only                                           | Same default population as other domains; `rollout_service_backlog`.                  |
| `LiquidityLadderWorld`                          | O(archetypes); NumPy rollout only                                           | `rollout_liquidity_ladder`; frozen bundle `liquidity_ladder_rollout_v1`.              |
| `InventoryBufferWorld`                          | O(archetypes); NumPy rollout only                                           | `rollout_inventory_buffer`; frozen bundle `inventory_buffer_rollout_v1`.              |
| GA / MC inner loop                              | O(population × horizon × steps)                                             | Wall-clock ∝ parallel `eval_workers` only when work is CPU-parallel **and** isolated. |


## CI vs optional jobs

- Default CI matrix stays on **NumPy** reference paths.
- **Numba parity** is an optional job / local install (`[accelerate]`); see `.github/workflows/ci.yml` and `tests/test_resource_cascade_numba_parity.py`.

## Benchmarks (frozen suite, Phase H charter)

- Golden bundles are **small** and intended for **regression**, not production-scale stress.
- `benchmark_rollout.py` measures wall-clock; numbers are **machine-dependent**. Compare **relative** speedups under identical flags.

## Robustness sweeps and composite artifacts

- `**fragility_robustness_sweep.py --topology dense|neighbor_lists`** — same ER/WS draws; `**neighbor_lists**` keeps **O(edges)** topology RAM while matching dense rollouts bit-for-bit for the same adjacency (see tests).
- **2D grids** (`fragility-robustness-sensitivity-2d-v1`) scale as **|values_x| × |values_y| × |graph_seeds|** rollouts — keep grids tiny for exploration.
- `**neighbor_json_bundle`**: ensemble size is **number of JSON files**; each path is loaded via `load_neighbor_topology` (same format as Phase I counterfactual CLIs).
- **GA budget sweep** (`fragility-robustness-ga-budget-1d-v1`): cost scales as **sum over generation budgets** of **(population × generations × rollout cost)** plus one ensemble evaluation per budget point — keep `**--ga-generations-values`** tiny for exploration.
- **GA budget 2D grid** (`fragility-robustness-ga-budget-2d-v1`): **|generations| × |populations|** inner GA runs each with its own derived seed; keep both axes small.
- **GA population 1D sweep** (`fragility-robustness-ga-population-1d-v1`): **|population_sizes|** inner GA runs at fixed `**ga_generations_fixed`**; supports `**neighbor_json_bundle**` (`--neighbor-json-list` on `fragility_robustness_sweep.py`).
- **Institutional composite** (`fragility-institutional-composite-v1` / **v2** / **v3**): one schedule, **N** independent kernel rollouts — wall-clock ≈ sum of those rollouts (no cross-kernel state).
- **Pareto hypervolume (2-D min):** `hypervolume_2d_min` is **O(n²)** non-dominated filter + linear sweep in **n**; safe only for modest archive sizes (use sampling for huge fronts).

## Communicating impact responsibly

What moves perception is not bigger graphs by default, but **frozen artifacts + manifest + certificate + one guided workflow** — see `[PAPER_APPENDIX_WORKFLOW.md](PAPER_APPENDIX_WORKFLOW.md)` and `scripts/run_flagship_demo.py`.