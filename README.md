# Fragility Discovery Engine

[![CI](https://github.com/theorem6/fragility-discovery-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/theorem6/fragility-discovery-engine/actions/workflows/ci.yml)

Autonomous **coverage-guided-style** search over a modular simulation: mutate shock schedules, maximize instability metrics, then extract **minimal collapse sequences** and causal replay artifacts.

## Layout (four engines)

| Layer | Role |
|--------|------|
| `fragility_engine.world` | Domain physics only — no attacker concepts. |
| `fragility_engine.agents` | Behavior archetypes — `observe → decide → act`. |
| `fragility_engine.adversary` | Deterministic search (Monte Carlo + GA) over shock schedules. |
| `fragility_engine.explain` | Ablation / minimization / **counterfactual** bundles. |
| `fragility_engine.network` | ``ContagionGraph`` + topology; contagion uses **neighbor lists** (**O(edges)** per step, dense adjacency storage unchanged). |
| `fragility_engine.coevolution` | Alternating attacker/defender search; aggregate + network + `alternating_coevolution_rollout` hook for custom worlds. |

Phase 1 is **deterministic** (fixed NumPy RNG seeds). LLM policies stay out until the core loop is proven.

**Scope creep guardrail:** read [`BOUNDARIES.md`](BOUNDARIES.md) before adding agents, graph models, multi-objective fitness, UI, or defender loops.

**Where we go next (aspirational):** [`ROADMAP_NEXT.md`](ROADMAP_NEXT.md) — phases I–L plus moonshots; **Phase H** (benchmark harness + ensemble robustness slice) is **normative** in [`BOUNDARIES.md`](BOUNDARIES.md). **Phase L** (narration + publication CLI): [`docs/phase_l_publication.md`](docs/phase_l_publication.md).

**Phase J (second domain narrative):** [`docs/WHY_RESOURCE_CASCADE.md`](docs/WHY_RESOURCE_CASCADE.md) — why `ResourceCascadeWorld` exists and what we do *not* claim. Worked counterfactual commands: [`docs/resource_cascade_counterfactual_example.md`](docs/resource_cascade_counterfactual_example.md).

**Reproducible benchmarks:** [`benchmarks/README.md`](benchmarks/README.md) — `python scripts/run_benchmark_suite.py --validate`.

## Quick start

```powershell
cd C:\Users\david\projects\fragility-discovery-engine
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
python scripts/week1_smoke.py
python scripts/run_ga_demo.py
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/week1_smoke.py` | Deterministic rollout smoke (`--export-replay`, `--initial-panic`, `--continue-after-collapse`) |
| `scripts/run_mc_demo.py` | Monte Carlo random schedules (`--export-replay`, `--continue-after-collapse`) |
| `scripts/export_minimized_replay.py` | Random collapsing schedule → greedy minimization → replay JSON |
| `scripts/run_ga_demo.py` | GA + greedy minimization (`--export-replay`, `--export-minimized-replay`, `--generations`, `--population-size`, `--seed`) |
| `scripts/run_resource_cascade_ga_demo.py` | Phase **J** scaffold: GA + minimization on **`ResourceCascadeWorld`** (`--initial-overload`, same export flags); see [`docs/phase_j_resource_cascade.md`](docs/phase_j_resource_cascade.md) |
| `scripts/run_network_demo.py` | GA on **graph contagion** (`--graph-kind`, `--neighbor-json` / `--neighbor-weights-json`, `--export-replay`, sizing flags) |
| `scripts/export_replay.py` | `replay.json`: aggregate (`--initial-panic`, `--continue-after-collapse`), network (`--base-panic`, synthetic topology **or** `--neighbor-json`, `--continue-after-collapse`), or **`resource_cascade`** (`--initial-overload`, `--continue-after-collapse`) |
| `scripts/fragility_surface.py` | CSV fragility grid; `--panic-*`, `--depeg-*`, `integral_instability` column |
| `scripts/run_coevolution.py` | Alternating attacker/defender GA: `--mode aggregate|network|resource_cascade`, **`--initial-overload`** (cascade mode), `--continue-after-collapse`, topology flags or `--neighbor-json`, `--collect-attacker-pareto`, **`--export-pareto-json`** (viewer-ready `pareto-front-v1`), `--json-summary`, `--export-replay` |
| `scripts/export_coevolution_pareto.py` | Convert `--json-summary` output → `pareto_front.json` (`--from-summary`, `--out`) |
| `scripts/export_pareto_front.py` | `pareto_front.json`; **`--mode aggregate|network|resource_cascade`** (**`--initial-overload`** for cascade); topology / `--neighbor-json` for network; GA sizing `--horizon`, `--generations`, `--population-size`; `--export-replay` (+ `--replay-pareto-index`) |
| `scripts/find_cheap_collapse.py` | Cost-penalized GA (`--export-replay`) |
| `scripts/export_counterfactual.py` | Attribution JSON; **`--mode aggregate|network|resource_cascade`**; cascade: `remove_steps`, **`initial_overload_shift`**, **`cascade_coupling_shift`** (`--variant-cascade-coupling`); network shifts (`base_panic_shift`, …); [`docs/network_counterfactual_example.md`](docs/network_counterfactual_example.md), [`docs/resource_cascade_counterfactual_example.md`](docs/resource_cascade_counterfactual_example.md) |
| `scripts/export_counterfactual_chain.py` | Ordered mutation chain counterfactual + optional **`--emit-path-trace`** (`explanation-mutation-chain-path-v1`) |
| `scripts/export_resource_cascade_counterfactual_chain.py` | Phase **J**: **`ResourceCascadeWorld`** cumulative physics chain (`resource-cascade-mutation-chain-spec-v1`) + optional **`--emit-path-trace`** (`explanation-mutation-chain-path-resource-cascade-v1`) |
| `scripts/export_resource_cascade_joint_attribution.py` | **`attribution-merge-v1`**: shared-baseline **remove_steps** + **`--second-branch`** **initial_overload_shift** or **cascade_coupling_shift** |
| `scripts/narrate_frozen_json.py` | Phase **L**: replay / Pareto / merge / epsilon-sweep JSON; **`--cite-digest`**; **`--json-out`** → **`narration-summary-v1`** (core narration lives in **`fragility_engine.explain.narration`**) |
| `scripts/export_llm_narration_prompt.py` | Phase **L**: **`llm-prompt-bundle-v1`**; **`--prompt-pack`** `narration_v1` \| `reviewer_memo_v1` \| `paper_appendix_v1`; optional **`--invoke-openai`** **`--max-tokens`** |
| `scripts/plot_replay_timeline.py` | Replay: **`metrics.price`** / **`metrics.instability`** vs timestep; **`fragility-plot-style-v1`** |
| `scripts/plot_epsilon_sweep.py` | **`counterfactual-epsilon-sweep-v1`** curve + collapse markers; **`fragility-plot-epsilon-sweep-style-v1`** |
| `scripts/plot_pareto_front.py` | **`pareto-front-v1`**: severity vs attack_cost; **`fragility-plot-pareto-style-v1`** |
| `scripts/plot_fragility_surface_csv.py` | **`fragility_surface.py`** CSV heatmap (**panic0** × **depeg_threshold**); **`fragility-plot-surface-style-v1`** |
| `scripts/plot_counterfactual_bars.py` | **`export_counterfactual`** JSON: grouped bars (**integral_instability**, **attack_cost**) baseline vs counterfactual; **`fragility-plot-counterfactual-style-v1`** |
| `scripts/merge_counterfactual_attribution.py` | Star-merge exports → **`attribution-merge-v1`** |
| `scripts/summarize_attribution_merge.py` | **`attribution-interaction-summary-v1`** (sum of branch deltas + disclaimer) |
| `scripts/frozen_json_digest.py` | SHA-256 fingerprints for frozen JSON (`--json-out`) |
| `scripts/compare_replays.py` | Print JSON diff of top-level replay metrics + **`metric_notes`** (price/headroom semantics); optional `--out` |
| `scripts/regenerate_test_exports.ps1` / `scripts/regenerate_test_exports.sh` | Fill `artifacts/test_exports/` for browser QA (gitignored) |
| `scripts/benchmark_rollout.py` | Wall-clock: **`--bundle <phase_h_id>`**, **`--bundle-all`** (full Phase H suite JSON), or **ad-hoc** `--mode aggregate|network|resource_cascade` (`--json`, **`workflow`** field) |
| `scripts/run_benchmark_suite.py` | Phase **H** golden bundles (`--validate`, `--json`, **`--manifest-out`**) — see [`benchmarks/README.md`](benchmarks/README.md) |
| `scripts/fragility_robustness_sweep.py` | Moonshot: ensemble metrics over **`graph_seed`** (`--json`, topology sizing) |
| `scripts/counterfactual_epsilon_sweep.py` | **`--mode aggregate|network|resource_cascade`**; axes **`initial_panic`** / **`initial_overload`** / network scalars; **`--emit-trace`** → `explanation-trace-v1`; [`docs/network_counterfactual_example.md`](docs/network_counterfactual_example.md), cascade cookbook [`docs/resource_cascade_counterfactual_example.md`](docs/resource_cascade_counterfactual_example.md) |

**Plot scripts** (`plot_*.py`) require **`matplotlib`** (`pip install -e ".[dev]"` or **`.[viz]`**).

Static **replay** UI: `artifacts/replay_viewer/index.html` — scrub timeline, keyboard arrows, optional second JSON for A/B deltas; optional URL hash `#src=…&compare=…` (HTTP).

Local **bulk exports** for trying many scenarios in the browser: run `pwsh -File scripts/regenerate_test_exports.ps1` → writes under `artifacts/test_exports/` (gitignored). See `artifacts/README_test_exports.txt`.

Static **Pareto** UI: `artifacts/pareto_viewer/index.html` — load `pareto_front.json` (from `scripts/export_pareto_front.py`); bundled `sample_pareto_front.json` + **`sample_pareto_resource_cascade.json`**; HTTP **Presets** via `local_presets.json`; hover / click / arrows; optional hash `#src=…&archive=N`. Archive JSON includes `integral_instability` per point.

Static **attribution** UI: `artifacts/attribution_viewer/index.html` — `attribution-merge-v1` and mutation-chain path traces.

## Extending

- **Custom co-evolution:** implement a deterministic ``rollout_fn(schedule, seed, defender)`` and pass it to ``fragility_engine.coevolution.alternating_coevolution_rollout`` (see [`BOUNDARIES.md`](BOUNDARIES.md) Phase G).
- **Custom topology:** ``ContagionGraph.from_neighbor_lists([[...], ...])`` builds from adjacency lists (symmetrized by default). For **directed out-neighbor lists** without a dense matrix, pass JSON via ``--neighbor-json`` (optional ``--neighbor-weights-json``); replay metadata uses ``neighbor_lists_topology_meta`` (`storage: neighbor_lists`). Synthetic graphs still attach ``undirected_edges`` + ``storage: dense_adjacency``.
- **Perf gate:** CI sets ``FRAGILITY_PERF_GATE=1`` and ``FRAGILITY_PERF_GATE_MS`` (240s default in `.github/workflows/ci.yml`). Locally, default ``pytest`` skips that test unless you set the env vars.

## Week roadmap (suggested)

1. CLI smoke + collapse metric — `scripts/week1_smoke.py`
2. Evolutionary adversary — `scripts/run_ga_demo.py`
3. Network contagion — `fragility_engine.network` + `StablecoinNetworkWorld`
4. Replay JSON — `runner.rollout_to_replay_dict` (`schema_version` **0.4.0**, includes `events_lane`)
5. Static replay / Pareto viewers (`artifacts/*/viewer`) consume frozen JSON; richer web UI remains optional.
