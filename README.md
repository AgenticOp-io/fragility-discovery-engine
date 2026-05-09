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
| `scripts/run_network_demo.py` | GA on **graph contagion** (`--graph-kind`, `--neighbor-json` / `--neighbor-weights-json`, `--export-replay`, sizing flags) |
| `scripts/export_replay.py` | `replay.json`: aggregate (`--initial-panic`, `--continue-after-collapse`) or network (`--base-panic`, synthetic topology flags **or** `--neighbor-json`, `--continue-after-collapse`) |
| `scripts/fragility_surface.py` | CSV fragility grid; `--panic-*`, `--depeg-*`, `integral_instability` column |
| `scripts/run_coevolution.py` | Alternating attacker/defender GA: `--mode aggregate|network`, `--continue-after-collapse`, topology flags or `--neighbor-json`, `--collect-attacker-pareto`, **`--export-pareto-json`** (viewer-ready `pareto-front-v1`), `--json-summary`, `--export-replay` |
| `scripts/export_coevolution_pareto.py` | Convert `--json-summary` output → `pareto_front.json` (`--from-summary`, `--out`) |
| `scripts/export_pareto_front.py` | `pareto_front.json`; **`--mode aggregate|network`** (topology / `--neighbor-json`); GA sizing `--horizon`, `--generations`, `--population-size`; `--export-replay` (+ `--replay-pareto-index`) |
| `scripts/find_cheap_collapse.py` | Cost-penalized GA (`--export-replay`) |
| `scripts/export_counterfactual.py` | Attribution JSON; **`--mode aggregate|network`** (topology flags or `--neighbor-json`); `--export-replay-dir` → `baseline.json` + `counterfactual.json` |
| `scripts/compare_replays.py` | Print JSON diff of top-level metrics for two replay files; optional `--out` |
| `scripts/regenerate_test_exports.ps1` / `scripts/regenerate_test_exports.sh` | Fill `artifacts/test_exports/` for browser QA (gitignored) |
| `scripts/benchmark_rollout.py` | Wall-clock timing for aggregate vs network rollouts (`--json`, sizing flags, optional `--neighbor-json`) |

Static **replay** UI: `artifacts/replay_viewer/index.html` — scrub timeline, keyboard arrows, optional second JSON for A/B deltas; optional URL hash `#src=…&compare=…` (HTTP).

Local **bulk exports** for trying many scenarios in the browser: run `pwsh -File scripts/regenerate_test_exports.ps1` → writes under `artifacts/test_exports/` (gitignored). See `artifacts/README_test_exports.txt`.

Static **Pareto** UI: `artifacts/pareto_viewer/index.html` — load `pareto_front.json` (from `scripts/export_pareto_front.py`); bundled `sample_pareto_front.json`; HTTP **Presets** via `local_presets.json`; hover / click / arrows; optional hash `#src=…&archive=N`. Archive JSON includes `integral_instability` per point.

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
