# Phase H benchmark bundles

**New user?** Start with [`docs/HOW_TO_USE.md`](../docs/HOW_TO_USE.md) (install + tutorial paths), then return here for bundle IDs and exploration CLIs.

This folder documents **frozen deterministic bundles** implemented in code:

- `fragility_engine.benchmarks.suite` — five bundles (`aggregate_rollout_v1`, `network_er_rollout_v1`, `network_neighbor_list_rollout_v1`, **`resource_cascade_rollout_v1`**, **`service_backlog_rollout_v1`** — Phase M third domain).
- Golden scalars live beside the runners (`GOLDEN_METRICS`); CI asserts relaxed numerical agreement.

## Reproduce locally

```powershell
cd fragility-discovery-engine
pip install -e ".[dev]"
python scripts/run_benchmark_suite.py --validate
```

JSON output (no validation):

```powershell
python scripts/run_benchmark_suite.py --json
```

Portable inventory (`benchmark-manifest-v2`: per-bundle topology, provenance, `golden_metrics_sha256`, pointers to hypervolume + explanation DAG tooling):

```powershell
python scripts/run_benchmark_suite.py --manifest-out artifacts/benchmark_manifest.json
```

2-objective **minimization hypervolume** (for Pareto-style archives): `fragility_engine.benchmarks.hypervolume.hypervolume_2d_min`. **Mechanical DAG** JSON: `scripts/export_explanation_dag.py` (from counterfactual JSON or a greedy minimization report — use `export_minimized_replay.py --minimization-report-out` to capture the latter).

The manifest includes **`resource_cascade_backend`** (`resource_cascade_backend_env`, `resource_cascade_backend_effective`) for the same pinned `ResourceCascadeWorld` template as bundle `resource_cascade_rollout_v1`, matching `scripts/benchmark_rollout.py --json` semantics.

## Cite a bundle

Use the bundle id, pinned seeds documented in `suite.py` (`PINNED_GENOME_SEED`, `PINNED_ROLLOUT_SEED`), and record:

- `fragility-engine` git commit SHA,
- Python version,
- `numpy` version.

Example citation fragment:

> Reproduced with `fragility-discovery-engine` bundle `network_er_rollout_v1` at commit `<SHA>` using `python scripts/run_benchmark_suite.py --validate`.

## Robustness, GA budgets, mechanism design, composites

Topology dispersion for a **fixed** attacker genome:

```powershell
python scripts/fragility_robustness_sweep.py --json --graph-seeds 101,102,103
```

Schema: `fragility-robustness-ensemble-v1` (see `fragility_engine.benchmarks.ensemble`). Payload includes **`topology_representation`** (`dense` \| `neighbor_lists`).

**List topology (matches dense per draw):**

```powershell
python scripts/fragility_robustness_sweep.py --json --topology neighbor_lists --graph-seeds 101,102,103
```

**1D sensitivity (collapse rate vs one knob):** same graph seeds at each step; scans `er_p`, `ws_p`, `ws_k`, `base_panic`, `contagion_beta`, or `whale_frac`. Nested schema `fragility-robustness-sensitivity-1d-v1`:

```powershell
python scripts/fragility_robustness_sweep.py --json --graph-seeds 101,102,103 --sweep-param er_p --sweep-values 0.08,0.12,0.16
```

**2D grid:** `--sweep-param` / `--sweep-values` plus **`--sweep-param-2`** / **`--sweep-values-2`** (distinct params). Schema `fragility-robustness-sensitivity-2d-v1`:

```powershell
python scripts/fragility_robustness_sweep.py --json --graph-seeds 101,102 --sweep-param er_p --sweep-values 0.10,0.14 --sweep-param-2 base_panic --sweep-values-2 0.04,0.07
```

**Neighbor-json bundle (fixed list topologies):** each JSON file is one ensemble member (`topology_mode: neighbor_json_bundle`). **`--graph-seeds`** is ignored. Optional per-file weights: **`--neighbor-weights-json-list`** with the same number of comma-separated paths; use **`none`** or **`-`** for slots without weights.

```powershell
python scripts/fragility_robustness_sweep.py --json --neighbor-json-list path/topA.json,path/topB.json --sweep-param contagion_beta --sweep-values 0.30,0.36
```

**GA budget sweep** (train attacker on one topology / first neighbor JSON; ensemble-evaluate): schema **`fragility-robustness-ga-budget-1d-v1`**:

```powershell
python scripts/fragility_robustness_sweep.py --json --ga-budget-sweep --ga-generations-values 2,4,8 --graph-seeds 101,102,103 --ga-population-size 16
```

**GA budget 2D grid** (generations × population): **`fragility-robustness-ga-budget-2d-v1`** — cost scales as **|G| × |P| × inner GA cost**:

```powershell
python scripts/fragility_robustness_sweep.py --json --ga-budget-2d --ga-generations-values 2,4 --ga-population-values 12,16 --graph-seeds 101,102
```

**GA population 1D sweep** (fixed generations): **`fragility-robustness-ga-population-1d-v1`**:

```powershell
python scripts/fragility_robustness_sweep.py --json --ga-population-sweep --ga-population-values 12,16,20 --ga-fixed-generations 4 --graph-seeds 101,102,103
```

**Mechanism design (outer discrete policies):**

```powershell
python scripts/mechanism_design_policy_sweep.py --json --policies weak,mid,strong,reserve_focus,panic_focus
```

**Institutional composite** (same schedule, **decoupled** kernels — not a coupled mega-model):

```powershell
# Twin (network + resource cascade) → fragility-institutional-composite-v1
python scripts/institutional_composite_demo.py --out artifacts/tmp/composite.json
# + aggregate peg → v2 (--aggregate-seed, --aggregate-initial-panic)
python scripts/institutional_composite_demo.py --triple --out artifacts/tmp/composite_v2.json
```

Composite JSON is **not** loadable in the static **replay** timeline viewer — see [`artifacts/replay_viewer/README.md`](../artifacts/replay_viewer/README.md).

## Wall-clock timing (Phase K helper)

Compare machines or commits using the **same frozen workload** as CI golden bundles (not a regression gate):

```powershell
python scripts/benchmark_rollout.py --bundle aggregate_rollout_v1 --repeat 16 --warmup 2 --json
python scripts/benchmark_rollout.py --bundle resource_cascade_rollout_v1 --repeat 16 --json
python scripts/benchmark_rollout.py --bundle-all --repeat 16 --warmup 2 --json
```

Optional **search timing** (Monte Carlo or GA on bundle worlds, same pinned horizon as suite genomes): `--bench-search mc|ga` with `--bundle` or `--bundle-all`, plus `--eval-workers`, **`--eval-pool threads|processes`**, `--search-samples` / `--search-generations`, `--search-population`. Emits `workflow: "phase_h_bundle_search_microbench"`.

From the suite driver: **`python scripts/run_benchmark_suite.py --bench-search ga|mc`** (same flags: `--eval-workers`, `--eval-pool`, `--search-generations`, `--search-population`, `--search-samples`, `--search-seed`) runs **`run_phase_h_search_microbench`** once over all bundles (no repeat/warmup loop).

## Citation bundle (`fragility-certificate-v1`)

Machine-readable environment + artifact digests (not a legal certificate):

```powershell
python scripts/export_fragility_certificate.py --out cite.json --digest-json replay.json pareto.json --validate-bundles
```

Or generate replay + Pareto + certificate together:

```powershell
python scripts/run_flagship_demo.py --out-dir artifacts/flagship/output
```

Schema constant: `fragility_engine.benchmarks.certificate.FRAGILITY_CERTIFICATE_SCHEMA`. Workflow: [`docs/PAPER_APPENDIX_WORKFLOW.md`](../docs/PAPER_APPENDIX_WORKFLOW.md).

JSON includes `workflow: "phase_h_bundle"`, `bundle_id`, `pinned_genome_seed`, `pinned_rollout_seed`, and `mean_ms_per_rollout`. Resource-cascade bundles / suite / `ad_hoc` **`resource_cascade`** runs also include **`resource_cascade_backend`**: `resource_cascade_backend_env` and `resource_cascade_backend_effective` (NumPy vs Numba dispatch intent for `FRAGILITY_RESOURCE_CASCADE_BACKEND`). **`--bundle-all`** emits **`phase_h_bundle_suite`** with a `bundles` array plus `total_wall_clock_s`. Ad-hoc sizing continues to use `--mode` (`workflow: "ad_hoc"`). See [`docs/phase_k_acceleration.md`](../docs/phase_k_acceleration.md).
