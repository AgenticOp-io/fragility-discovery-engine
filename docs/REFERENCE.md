# Reference: modes, CLIs, environment, schemas

Quick lookup for operators and contributors. Tutorials and narrative context are in [`HOW_TO_USE.md`](HOW_TO_USE.md).

---

## Simulation modes

| `--mode` | GA demo script | Primary counterfactual interventions | ε-sweep axes |
|----------|----------------|--------------------------------------|--------------|
| `aggregate` | `run_ga_demo.py` | `remove_steps` | `initial_panic` |
| `network` | `run_network_demo.py` | `remove_steps`, `base_panic_shift`, `contagion_beta_shift`, edge weights | `base_panic`, `contagion_beta`, `edge_weight` |
| `resource_cascade` | `run_resource_cascade_ga_demo.py` | `remove_steps`, `initial_overload_shift`, `cascade_coupling_shift` | `initial_overload` |
| `service_backlog` | `run_service_backlog_ga_demo.py` | `remove_steps`, `initial_backlog_shift`, `process_rate_shift` | `initial_backlog`, `process_rate` |
| `liquidity_ladder` | `run_liquidity_ladder_ga_demo.py` | `remove_steps`, `initial_margin_shift`, `delever_rate_shift` | `initial_margin`, `delever_rate` |

Shared flags across most mode-aware scripts:

- `--horizon` — genome rows (schedule length)
- `--seed` / `--genome-seed` — rollout vs genome RNG
- `--export-replay PATH` — write replay JSON
- `--continue-after-collapse` — keep stepping after collapse for recovery metrics
- `--eval-workers N` — thread pool for GA/MC (clone worlds when N>1)

---

## Scripts by task

| Task | Script |
|------|--------|
| Smoke test | `week1_smoke.py` |
| Export one replay | `export_replay.py --mode …` |
| MC search | `run_mc_demo.py --mode …` |
| GA search | `run_ga_demo.py` or domain GA demos |
| Pareto front | `export_pareto_front.py --mode …` |
| Co-evolution | `run_coevolution.py --mode …` |
| Counterfactual pair | `export_counterfactual.py` |
| ε-sweep | `counterfactual_epsilon_sweep.py` |
| Mutation chain | `export_*_counterfactual_chain.py` (per domain) |
| Merge branches | `merge_counterfactual_attribution.py` |
| Frozen benchmarks | `run_benchmark_suite.py --validate` |
| Wall-clock timing | `benchmark_rollout.py --bundle …` or `--mode …` |
| Certificate | `export_fragility_certificate.py` |
| Flagship demo bundle | `run_flagship_demo.py` |
| Narration | `narrate_frozen_json.py` |
| Local CI parity | `ci_local.sh` / `ci_local.ps1` |

Full one-line descriptions: root [`README.md`](../README.md) scripts table.

---

## Frozen benchmark bundles (Phase H)

| `bundle_id` | Topology / domain |
|-------------|-----------------|
| `aggregate_rollout_v1` | Scalar peg |
| `network_er_rollout_v1` | ER synthetic graph |
| `network_neighbor_list_rollout_v1` | Neighbor-list graph |
| `resource_cascade_rollout_v1` | Resource cascade |
| `service_backlog_rollout_v1` | Service backlog |
| `liquidity_ladder_rollout_v1` | Liquidity ladder |

Pinned seeds and golden metrics: `src/fragility_engine/benchmarks/suite.py`. Validate with:

```bash
python scripts/run_benchmark_suite.py --validate
```

---

## Environment variables

| Variable | Default | Effect |
|----------|---------|--------|
| `FRAGILITY_PERF_GATE` | unset (off locally) | When `1`, enables slow benchmark perf test in pytest |
| `FRAGILITY_PERF_GATE_MS` | `240000` in CI | Wall-clock ceiling for perf gate (ms) |
| `FRAGILITY_RESOURCE_CASCADE_BACKEND` | `numpy` | `numpy` or `numba` for resource cascade rollouts |
| `FRAGILITY_CI_LOCAL_BUILD` | unset | When `1`, `ci_local` also runs `python -m build` |
| `FRAGILITY_GCE_INSTANCE` | — | VM name for `gce_sync_vm.ps1` |
| `FRAGILITY_GCE_ZONE` | — | GCE zone for sync scripts |
| `FRAGILITY_GCE_PROJECT` | — | GCP project id |
| `FRAGILITY_DEPLOY_DIR` | `~/fragility-discovery-engine` | GCE clone path |
| `FRAGILITY_REPO_URL` | GitHub SSH URL | GCE git remote when deploy key present |

---

## Common JSON schemas

| Schema id | Produced by | Consumed by |
|-----------|-------------|---------------|
| Replay (`schema_version` e.g. `0.4.0`) | `rollout_to_replay_dict` | Replay viewer, narration |
| `pareto-front-v1` | `export_pareto_front`, coevolution | Pareto viewer |
| `fragility-certificate-v1` | `export_fragility_certificate` | Papers, audit |
| `benchmark-manifest-v2` | `run_benchmark_suite.py --manifest-out` | CI artifact, appendix |
| `attribution-merge-v1` | merge / joint export scripts | Attribution viewer |
| `counterfactual-epsilon-sweep-v1` | `counterfactual_epsilon_sweep.py` | Plots, narration |
| `explanation-dag-v1` | `export_explanation_dag.py` | Narration |
| `narration-summary-v1` | `narrate_frozen_json.py --json-out` | External reports |
| `fragility-institutional-composite-v1` … `v3` | `institutional_composite_demo.py` | Composite viewer |
| `llm-prompt-bundle-v1` | `export_llm_narration_prompt.py` | External LLM only |

**Important:** composite, sweep, and Pareto JSON are **not** replay timelines. Loading them in `artifacts/replay_viewer/` will fail by design.

---

## Repository layout (operator view)

```
fragility-discovery-engine/
  src/fragility_engine/     Library code
  scripts/                  CLI tools
  tests/                    Pytest (400+ tests)
  benchmarks/               Benchmark docs + fixtures pointers
  artifacts/                Checked-in demo JSON + static HTML viewers
  docs/                     This documentation set
  BOUNDARIES.md             Charter and phase gates
  pyproject.toml            Package metadata and extras: dev, viz, accelerate
```

Python package name on PyPI-style installs: `fragility-engine` (import `fragility_engine`).
