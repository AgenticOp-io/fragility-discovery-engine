# Scale, complexity, and determinism (honest limits)

This document states **what scales how** and **what breaks reproducibility** if misused. It complements [`phase_k_acceleration.md`](phase_k_acceleration.md) (optional backends + threading/process pools).

## Determinism

- **Same seed, same code path, same NumPy reference rollout** ⇒ same trajectory (modulo documented FP tolerances on some bundles).
- **Parallel evaluation** (`eval_workers > 1`) is deterministic **only** when each task owns isolated mutable state (see `coevolution.thread_safe_template` and clone helpers). Sharing one `AgentPopulation` across threads races.
- **`eval_pool="processes"`** requires a **picklable** `rollout_fn` (e.g. `functools.partial(rollout_bundle_with_genome, bundle_id, isolate=True)`). Arbitrary closures from demo scripts will fail pickle on Windows spawn.

## Asymptotics (per timestep mental model)

| Piece | Dominant cost | Notes |
|--------|----------------|--------|
| `StablecoinNetworkWorld` step (dense adjacency) | O(n²) mixing in worst case; **neighbor-list** path is **O(edges)** per step | Prefer list topology for large n. |
| `StablecoinPegWorld` | O(archetypes) | Aggregate reference. |
| `ResourceCascadeWorld` | O(archetypes); optional Numba path | See `FRAGILITY_RESOURCE_CASCADE_BACKEND`. |
| GA / MC inner loop | O(population × horizon × steps) | Wall-clock ∝ parallel `eval_workers` only when work is CPU-parallel **and** isolated. |

## CI vs optional jobs

- Default CI matrix stays on **NumPy** reference paths.
- **Numba parity** is an optional job / local install (`[accelerate]`); see `.github/workflows/ci.yml` and `tests/test_resource_cascade_numba_parity.py`.

## Benchmarks (Phase H)

- Golden bundles are **small** and intended for **regression**, not production-scale stress.
- `benchmark_rollout.py` measures wall-clock; numbers are **machine-dependent**. Compare **relative** speedups under identical flags.

## “Game changing” without lying

What moves perception is not bigger graphs by default, but **frozen artifacts + manifest + certificate + one guided workflow** — see [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md) and `scripts/run_flagship_demo.py`.
