# Phase K — acceleration scaffold (design notes)

Phase K is defined at a high level in [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) (*honest performance & optional accelerated backends*). This document records **hook points** and **non-goals** so experiments do not fork semantics silently.

## Goals

- Preserve **bitwise determinism per seed** for the NumPy reference path (current default).
- Allow **optional** faster backends only behind explicit configuration, with **golden parity** against existing bundles (especially the frozen `*_rollout_v1` IDs in `fragility_engine.benchmarks.suite`, defined under Phase H in `BOUNDARIES.md`).
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
| Search | `monte_carlo_search` / `genetic_search` / `genetic_vector_search` / co-evolution | `eval_workers` + `eval_pool` (`threads` \| `processes`); threads use `thread_pool_map_ordered`. Process pool pickling requires a **picklable** `rollout_fn` (bundle helper: `partial(rollout_bundle_with_genome, id, isolate=True)`). MC pre-draws genomes then evaluates `(genome, seed + 2 + i)`. |

## Batch evaluation (`parallel_rollouts`)

Independent rollouts can be evaluated concurrently **without changing per-seed results** only when each task owns its mutable simulation state.

- **API (threads):** `fragility_engine.parallel_rollouts.thread_pool_map_ordered(fn, items, max_workers=None)` — thin `ThreadPoolExecutor.map` wrapper; **output order matches `items`** (same contract as sequential ``list(map(fn, items))`` when tasks are isolated).
- **GA:** `genetic_search(..., eval_workers=N)` and `genetic_vector_search(..., eval_workers=N)` evaluate each generation’s population with that pool size (`N=1` is sequential). Seeds stay **`seed + 1000 + gen * population_size + idx`** (attacker GA) and **`seed + 2000 + …`** (defender vector GA). Cli scripts accept **`--eval-workers`**; built-in evaluators clone worlds via `coevolution.thread_safe_template` when `N > 1`.
- **MC:** `monte_carlo_search(..., eval_workers=N)` draws **`samples`** genomes with the same RNG stream as before, then evaluates rollouts at **`seed + 2 + i`**. **`scripts/run_mc_demo.py --eval-workers`** mirrors the GA demos (peg clone when `N > 1`).
- **Shared templates:** `clone_resource_cascade` / defended builds often **reuse** `AgentPopulation` by reference; advancing one clone’s population can race another thread. Prefer a **fresh** world template inside each `fn(item)` (see `tests/test_parallel_rollouts.py`).
- **API (processes):** `process_pool_map_ordered(fn, items, max_workers=None)` — `ProcessPoolExecutor.map`; **`fn` must be pickle-safe** (module-level callable). Prefer threads for rollout closures; use the process pool only when profiling justifies pickling overhead (Windows uses spawn).

## Optional environment flag pattern

Libraries often use an explicit toggle (examples: `FRAGILITY_BACKEND=numpy|numba`, `JAX_PLATFORM_NAME=cpu`). Any adoption here should:

1. Default to **NumPy** when unset.
2. Be mentioned in [`BOUNDARIES.md`](../BOUNDARIES.md) when behavior or tolerances change.
3. Keep **`pytest`** green on the default path in CI.

### `FRAGILITY_RESOURCE_CASCADE_BACKEND` (implemented)

| Value | Behavior |
|-------|----------|
| *(unset)* or `numpy` | Reference loop: `ResourceCascadeWorld.step` (deterministic default). |
| `numba` | JIT fast path when `numba` is installed and the population matches `default_stablecoin_population()` (aggregate redeem is inlined). |
| `auto` | Use Numba when eligible; otherwise NumPy. |

Install optional dependency: `pip install -e ".[accelerate]"` (declares `numba`). Parity tests live in `tests/test_resource_cascade_numba_parity.py` and **skip** when Numba is absent.

**CI:** `.github/workflows/ci.yml` includes a **`numba-parity`** job (Ubuntu, Python 3.12, `[dev,accelerate]`) that runs only those parity tests so the matrix stays on the reference NumPy path.

**Platform caveat:** Numba publishes wheels for many **x86_64** targets (Linux, macOS, Windows **amd64**). **Native Windows ARM64** Python (`win_arm64`) often has **no** prebuilt `llvmlite`/`numba` wheels, so `pip install …[accelerate]` may fail while compiling from source.

**Windows on ARM (WoA):** Use the **same** setup as on any Windows PC: install CPython from the **Windows installer (64-bit)** link on [python.org](https://www.python.org/downloads/windows/). That build targets **x64 (amd64)**; on ARM hardware the OS runs it under **built-in x64 emulation** (automatic — not the old `.exe` → Properties → Compatibility tab). Then the usual `pip install -e ".[accelerate]"` pulls **win_amd64** wheels.

Helper (finds an amd64 `python.exe` and installs `[dev,accelerate]`):

```powershell
cd path\to\fragility-discovery-engine
.\scripts\install_accelerate_windows.ps1
```

Manual example if the interpreter lives under `%LOCALAPPDATA%\Programs\Python\Python312-x64\`:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312-x64\python.exe" -m pip install -e ".[dev,accelerate]"
& "$env:LOCALAPPDATA\Programs\Python\Python312-x64\python.exe" -m pytest tests/test_resource_cascade_numba_parity.py -q
```

Otherwise use the default NumPy rollout path, or run Numba parity in CI / Linux / x64 environments.

## Exit criteria (reminder)

Promotion in `BOUNDARIES.md` should stay tied to **honest** reporting: optional backends remain off by default in CI; relative timings are measured via the harness above (and parity tests when Numba is installed), not assumed from prose.

## Named frozen bundles (`--bundle`)

Same bundle IDs as **`fragility_engine.benchmarks.suite`** / Phase H in [`BOUNDARIES.md`](../BOUNDARIES.md).

`scripts/benchmark_rollout.py --bundle <id>` times **exactly** the rollout body used by `fragility_engine.benchmarks.suite` / `run_benchmark_suite.py` (pinned genome + rollout seeds). Use this to document **relative** speedups when experimenting with optional backends—absolute ms vary by CPU/OS.

**Search microbench:** `--bench-search mc|ga` (requires `--bundle` or `--bundle-all`) runs `monte_carlo_search` or `genetic_search` on the same bundle templates via `bundle_search_evaluator` (`PINNED_SCHEDULE_HORIZON` rows). Pass **`--eval-workers`**, **`--eval-pool threads|processes`** (processes uses `functools.partial(rollout_bundle_with_genome, …, isolate=True)` for pickling), **`--search-generations`** / **`--search-population`** (GA), **`--search-samples`** (MC), **`--search-seed`**. JSON **`workflow`: `phase_h_bundle_search_microbench`** with per-bundle **`mean_ms_per_search`**.

**Suite CLI:** `python scripts/run_benchmark_suite.py --bench-search ga|mc [--eval-workers N] [--eval-pool processes] …` calls **`fragility_engine.benchmarks.suite.run_phase_h_search_microbench`** (same payload shape as `benchmark_rollout` microbench, without repeat/warmup loops).

| Bundle id | Domain workload |
|-----------|-----------------|
| `aggregate_rollout_v1` | `StablecoinPegWorld`, `max_steps=28`, 12-row pinned genome |
| `network_er_rollout_v1` | ER graph **n=16**, `max_steps=26`, same genome |
| `network_neighbor_list_rollout_v1` | 3-cycle neighbor lists, `max_steps=24` |
| `resource_cascade_rollout_v1` | `ResourceCascadeWorld`, `max_steps=26`, `initial_overload=0.05` |

Example:

```bash
python scripts/benchmark_rollout.py --bundle resource_cascade_rollout_v1 --repeat 8 --warmup 1 --json
```

Emit JSON includes `workflow`, `bundle_id`, `pinned_genome_seed`, `pinned_rollout_seed`, `mean_ms_per_rollout`. For **`resource_cascade_rollout_v1`**, **`--bundle-all`**, and ad-hoc **`--mode resource_cascade`**, JSON also includes **`resource_cascade_backend`** (`resource_cascade_backend_env`, `resource_cascade_backend_effective`) so timed runs record NumPy vs Numba dispatch intent.

### Comparing NumPy vs Numba (`resource_cascade_rollout_v1`)

Use the **same** bundle ID and repeat counts; only the environment flag changes. Install Numba first (`pip install -e ".[accelerate]"`) on a platform with wheels (many Linux x86_64 / macOS / Windows x64 builds; some ARM Windows setups lack wheels).

```bash
FRAGILITY_RESOURCE_CASCADE_BACKEND=numpy python scripts/benchmark_rollout.py \
  --bundle resource_cascade_rollout_v1 --repeat 16 --warmup 2 --json
FRAGILITY_RESOURCE_CASCADE_BACKEND=numba python scripts/benchmark_rollout.py \
  --bundle resource_cascade_rollout_v1 --repeat 16 --warmup 2 --json
```

PowerShell:

```powershell
$env:FRAGILITY_RESOURCE_CASCADE_BACKEND='numpy'
python scripts/benchmark_rollout.py --bundle resource_cascade_rollout_v1 --repeat 16 --warmup 2 --json
$env:FRAGILITY_RESOURCE_CASCADE_BACKEND='numba'
python scripts/benchmark_rollout.py --bundle resource_cascade_rollout_v1 --repeat 16 --warmup 2 --json
```

Divide the first run’s `mean_ms_per_rollout` by the second to get a **local** speedup factor (JIT warmup is included in `--warmup`; cold-start semantics match how you configure repeats).

**Reference NumPy snapshot** (informative, one developer machine, 2026): `resource_cascade_rollout_v1`, `--repeat 12 --warmup 2`, yielded `mean_ms_per_rollout` ≈ **0.37** ms. Re-run the command above on your CPU/OS before trusting ratios.

Suite sweep (every registered bundle, comparable relative timings on one machine):

```bash
python scripts/benchmark_rollout.py --bundle-all --repeat 8 --warmup 1 --json
```

JSON includes `workflow: "phase_h_bundle_suite"`, `bundles[]` per id, and `total_wall_clock_s`.

## Reference timing snapshot (informative, not a gate)

**Ad-hoc** workloads: wall-clock from `scripts/benchmark_rollout.py` (**NumPy** reference path, `--repeat 5 --warmup 1`, `horizon=24`, `max_steps=48`). Numbers vary by CPU/OS; use the same command to reproduce locally.

Example run (developer machine, 2026):

```json
{"workflow": "ad_hoc", "mode": "aggregate", "mean_ms_per_rollout": 0.381, "wall_clock_s": 0.00191}
{"workflow": "ad_hoc", "mode": "resource_cascade", "mean_ms_per_rollout": 0.484, "wall_clock_s": 0.00242, "initial_overload": 0.05}
```

Purpose: establish that **`resource_cascade`** rollouts stay in the same ballpark as aggregate at modest horizons before investing in optional backends.
