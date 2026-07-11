# Reference: modes, CLIs, environment, schemas

Quick lookup for all command-line flags, output formats, and script names. Step-by-step tutorials are in [How to Use](/docs/how-to-use.html).

---

## BYOW CLI (`fragility`, v0.6.0+)

| Command | Purpose |
|---------|---------|
| `fragility search --example capacity-pool\|token-bucket` | GA/MC on installable tutorial world |
| `fragility minimize --example …` | Greedy minimal failing schedule |
| `fragility replay PATH` | Validate replay JSON schema keys |
| `fragility check-world --example …` | Determinism smoke on example world |
| `fragility certify` | Flagship certificate bundle |
| `fragility falsify search --example ranked-store` | Predicate-violation search (Phase S) |
| `fragility examples` | List tutorial example ids |

Module surface: `fragility_engine.byow`, `fragility_engine.falsify`. Tutorial worlds: `fragility_engine.byow.examples.*`.

---

## Simulation modes

| `--mode` | GA demo script | Primary counterfactual interventions | ε-sweep axes | Fixed horizon |
|----------|----------------|--------------------------------------|--------------|---------------|
| `aggregate` | `run_ga_demo.py` | `remove_steps` | `initial_panic` | No |
| `network` | `run_network_demo.py` | `remove_steps`, `base_panic_shift`, `contagion_beta_shift`, edge weights | `base_panic`, `contagion_beta`, `edge_weight` | No |
| `resource_cascade` | `run_resource_cascade_ga_demo.py` | `remove_steps`, `initial_overload_shift`, `cascade_coupling_shift` | `initial_overload` | 18 |
| `service_backlog` | `run_service_backlog_ga_demo.py` | `remove_steps`, `initial_backlog_shift`, `process_rate_shift` | `initial_backlog`, `process_rate` | 18 |
| `liquidity_ladder` | `run_liquidity_ladder_ga_demo.py` | `remove_steps`, `initial_margin_shift`, `delever_rate_shift` | `initial_margin`, `delever_rate` | 18 |
| `inventory_buffer` | `run_inventory_buffer_ga_demo.py` | `remove_steps`, `initial_stock_shift` | `initial_stock` | 18 |

Flags shared across most scripts:

- `--horizon` — number of steps in the simulation (schedule length)
- `--seed` / `--genome-seed` — random seed for the rollout / for generating the initial schedule
- `--export-replay PATH` — save the result as a replay JSON file
- `--continue-after-collapse` — keep stepping after collapse, useful for measuring recovery
- `--eval-workers N` — number of parallel workers for the search (each gets its own world copy)

---

## Scripts by task

| Task | Script |
|------|--------|
| Smoke test | `week1_smoke.py` |
| Export one replay | `export_replay.py --mode …` |
| MC search | `run_mc_demo.py --mode …` |
| GA search (aggregate) | `run_ga_demo.py` |
| GA search (network) | `run_network_demo.py` |
| GA search (resource cascade) | `run_resource_cascade_ga_demo.py` |
| GA search (service backlog) | `run_service_backlog_ga_demo.py` |
| GA search (liquidity ladder) | `run_liquidity_ladder_ga_demo.py` |
| GA search (inventory buffer) | `run_inventory_buffer_ga_demo.py` |
| Pareto front | `export_pareto_front.py --mode …` |
| Co-evolution (all modes) | `run_coevolution.py --mode …` |
| Counterfactual pair | `export_counterfactual.py` |
| ε-sweep | `counterfactual_epsilon_sweep.py` |
| Mutation chain (aggregate) | `export_aggregate_counterfactual_chain.py` |
| Mutation chain (resource cascade) | `export_resource_cascade_counterfactual_chain.py` |
| Mutation chain (service backlog) | `export_service_backlog_counterfactual_chain.py` |
| Mutation chain (liquidity ladder) | `export_liquidity_ladder_counterfactual_chain.py` |
| Generic mutation chain | `export_counterfactual_chain.py` |
| Joint attribution (resource cascade) | `export_resource_cascade_joint_attribution.py` |
| Joint attribution (service backlog) | `export_service_backlog_joint_attribution.py` |
| Joint attribution (liquidity ladder) | `export_liquidity_ladder_joint_attribution.py` |
| Triple attribution | `export_resource_cascade_triple_attribution.py` |
| Merge branches | `merge_counterfactual_attribution.py` |
| Explanation DAG | `export_explanation_dag.py` |
| Minimized replay | `export_minimized_replay.py` |
| Robustness sweep | `fragility_robustness_sweep.py` |
| Robustness stretch presets | `fragility_robustness_stretch.py --preset small` or `medium` or `large` |
| Fragility surface CSV | `fragility_surface.py --mode … --axis1 … --axis2 …` |
| Find cheapest collapse | `find_cheap_collapse.py --mode … --samples …` |
| Compare two replays | `compare_replays.py baseline.json counterfactual.json` |
| Mechanism design sweep | `mechanism_design_policy_sweep.py` |
| Institutional composite | `institutional_composite_demo.py --triple` or `--quad` |
| Coevolution Pareto export | `export_coevolution_pareto.py` |
| Frozen benchmarks | `run_benchmark_suite.py --validate` |
| Wall-clock timing | `benchmark_rollout.py --bundle … --mode …` |
| Certificate | `export_fragility_certificate.py` |
| Flagship demo bundle | `run_flagship_demo.py` |
| Narration | `narrate_frozen_json.py` |
| LLM prompt bundle | `export_llm_narration_prompt.py --bundle <name>` |
| Plot replay | `plot_replay_timeline.py` |
| Plot Pareto | `plot_pareto_front.py` |
| Plot counterfactual bars | `plot_counterfactual_bars.py` |
| Plot ε-sweep | `plot_epsilon_sweep.py` |
| Plot fragility surface | `plot_fragility_surface_csv.py` |
| Plot composite bars | `plot_institutional_composite_bars.py` |
| Summarize attribution merge | `summarize_attribution_merge.py` |
| Validate viewer presets | `validate_viewer_presets.py` |
| Check manifest digest | `check_manifest_digest.py` |
| Check manifest inventory | `check_manifest_inventory.py` |
| Check manifest summary | `check_manifest_summary.py` |
| Check bundled artifacts | `check_bundled_artifacts.py` |
| Check bundled Pareto HV | `check_bundled_pareto_hypervolume.py` |
| Check flagship bundle | `check_flagship_bundled.py` |
| Frozen JSON digest | `frozen_json_digest.py` |
| Regenerate viewer samples | `regenerate_bundled_viewer_samples.py` |
| GCE workbench publish | `gce_publish_workbench.sh` |
| GCE run server | `gce_run_server.py` (systemd service on GCE) |
| GCE write status | `gce_write_workbench_status.py` |
| Static dashboard export | `export_static_dashboard.py` |
| Inventory buffer counterfactual | `export_inventory_buffer_counterfactual_chain.py` |
| Inventory buffer mutation chain | `export_inventory_buffer_mutation_chain.py` |
| Local CI parity | `ci_local.sh` / `ci_local.ps1` |

One-line descriptions for every script: root [README.md](../README.md) scripts table.

---

## export_static_dashboard.py — local viewer index

Generates a minimal HTML index at `artifacts/dashboard/index.html` that links all four bundled viewers (Replay, Pareto, Attribution, Composite) using relative paths. Designed for **local use** — serve from the repository root with `python -m http.server` and open in a browser. Not needed on the GCE workbench (the hosted site already provides the same navigation).

```bash
# Generate the dashboard index
python scripts/export_static_dashboard.py

# Serve locally (open http://localhost:8765/artifacts/dashboard/index.html)
python -m http.server 8765
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--out PATH` | `artifacts/dashboard/index.html` | Output file path |
| `--manifest PATH` | none | Optional `benchmark_manifest.json` to embed a link in the page |

**When to use it:** after running a local batch of scripts that produce artifacts in `artifacts/`, run `export_static_dashboard.py` once to get a single clickable entry point to all viewers without needing to remember their paths. The GCE workbench provides the same experience for hosted runs.

---

## export_inventory_buffer_counterfactual_chain.py — inventory buffer counterfactual

Compares a baseline inventory-buffer rollout against a variant with one of three intervention types: remove shock steps, shift initial stock, or shift demand-spike gain.

```bash
# Remove first 3 shock timesteps (default)
python scripts/export_inventory_buffer_counterfactual_chain.py --out cf.json

# Shift initial stock from 0.88 to 0.60 (low-stock variant)
python scripts/export_inventory_buffer_counterfactual_chain.py \
  --variant-initial-stock 0.60 --out cf_stock.json

# Shift demand-spike gain (more aggressive demand)
python scripts/export_inventory_buffer_counterfactual_chain.py \
  --variant-demand-spike-gain 0.95 --out cf_demand.json

# Export baseline and counterfactual as replay JSON files
python scripts/export_inventory_buffer_counterfactual_chain.py \
  --variant-initial-stock 0.50 --export-replay-dir ./cf_replays
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--out PATH` | `counterfactual_inventory_buffer.json` | Output attribution JSON |
| `--seed INT` | 424244 | Rollout RNG seed |
| `--genome-seed INT` | 7 | Genome generation seed |
| `--horizon INT` | 18 | Attacker schedule length |
| `--initial-stock FLOAT` | 0.88 | Baseline normalized stock at reset |
| `--remove-timesteps LIST` | first 3 steps | Comma-separated 0-based indices to zero out |
| `--variant-initial-stock FLOAT` | none | Counterfactual reset stock (`initial_stock_shift` intervention) |
| `--variant-demand-spike-gain FLOAT` | none | Counterfactual demand-spike gain (`demand_spike_shift` intervention) |
| `--continue-after-collapse` | off | Keep stepping after stockout for recovery metrics |
| `--max-steps INT` | 40 | World horizon cap |
| `--export-replay-dir PATH` | none | Write `baseline.json` and `counterfactual.json` replay files here |

Supply at most one of `--variant-initial-stock` / `--variant-demand-spike-gain`. If neither is supplied the script uses `remove_steps`. Output is an `attribution-merge-v1`-compatible JSON readable by the Attribution viewer.

---

## export_inventory_buffer_mutation_chain.py — inventory buffer mutation chain

Applies an ordered list of physics mutations cumulatively on an inventory-buffer template, then compares baseline vs final clone. Optional path trace emits one rollout per cumulative prefix (Attribution viewer).

```bash
python scripts/export_inventory_buffer_mutation_chain.py \
  --chain-json tests/fixtures/chains/inventory_buffer_demand_fulfillment_chain.json \
  --emit-path-trace --out cf_ib_chain.json
```

Chain spec schema: `inventory-buffer-mutation-chain-spec-v1`. Step kinds include `demand_spike_gain`, `fulfillment_erosion`, `replenish_rate`, `stock_recovery`, `stockout_collapse`, `fulfillment_floor_collapse`, `recovery_stock`, `max_steps`.

---

## Frozen reference bundles

Each bundle has pinned seeds and known-good metric values that are checked on every CI run.

| `bundle_id` | Domain |
|-------------|--------|
| `aggregate_rollout_v1` | Aggregate peg |
| `network_er_rollout_v1` | Network (synthetic ER graph) |
| `network_neighbor_list_rollout_v1` | Network (neighbor-list topology) |
| `resource_cascade_rollout_v1` | Resource cascade |
| `service_backlog_rollout_v1` | Service backlog |
| `liquidity_ladder_rollout_v1` | Liquidity ladder |
| `inventory_buffer_rollout_v1` | Inventory buffer |

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

**Note:** composite, sweep, and trade-off chart (Pareto) files are **not** replay timelines. The replay viewer only accepts replay files — loading other types will show an error.

---

## Repository layout

```
fragility-discovery-engine/
  src/fragility_engine/     Library code (worlds, search, explanation, benchmarks)
  scripts/                  Command-line tools
  tests/                    Test suite (400+ tests)
  benchmarks/               Benchmark documentation and reference bundle definitions
  artifacts/                Bundled demo JSON files and browser-based viewers
  docs/                     This documentation set
  pyproject.toml            Package definition; extras: dev, viz, accelerate
```

Install with `pip install -e ".[dev]"`. Import name: `fragility_engine`.
