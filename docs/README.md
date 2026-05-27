# Documentation

This folder is the user and operator guide for the Fragility Discovery Engine. The root [`README.md`](../README.md) is a short project overview. Start here if you are installing, running CLIs, or reviewing artifacts.

Normative scope, phase gates, and hard non-goals live in [`BOUNDARIES.md`](../BOUNDARIES.md).

---

## Start here by role

| If you are… | Read first | Then |
|-------------|------------|------|
| **New to the project** | [`WHITEPAPER_INTRODUCTION.md`](WHITEPAPER_INTRODUCTION.md) | [`HOW_TO_USE.md`](HOW_TO_USE.md) |
| **Installing and running** | [`HOW_TO_USE.md`](HOW_TO_USE.md) §1–3 | [`INSTALLATION.md`](INSTALLATION.md) for platform-specific setup |
| **Looking up a CLI flag or schema** | [`REFERENCE.md`](REFERENCE.md) | Script `--help`, tests under `tests/` |
| **Reviewer / paper appendix** | [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md) | [`../benchmarks/README.md`](../benchmarks/README.md), [`BUNDLED_ARTIFACTS.md`](BUNDLED_ARTIFACTS.md) |
| **Understanding the architecture** | [`ARCHITECTURE.md`](ARCHITECTURE.md) | [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md), [`BOUNDARIES.md`](../BOUNDARIES.md) |

---

## Core reference

| Document | What it covers |
|----------|----------------|
| [`WHITEPAPER_INTRODUCTION.md`](WHITEPAPER_INTRODUCTION.md) | What the engine is, what problem it solves, the six domains, who it fits |
| [`HOW_TO_USE.md`](HOW_TO_USE.md) | Install, tutorials, all CLI scripts, viewers, troubleshooting |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Package layout, rollout pipeline, simulation modes, determinism |
| [`REFERENCE.md`](REFERENCE.md) | CLI flag matrix by mode, environment variables, JSON schema names |
| [`INSTALLATION.md`](INSTALLATION.md) | OS packages, Python version, Git credentials, CI parity scripts |
| [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md) | Complexity, parallelism, sweep cost, determinism caveats |
| [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md) | End-to-end path from run to citable artifact bundle |
| [`BUNDLED_ARTIFACTS.md`](BUNDLED_ARTIFACTS.md) | Checked-in JSON for viewers and CI pins |
| [`PROJECT_STATUS.md`](PROJECT_STATUS.md) | Charter + Phase O completion snapshot |
| [`phase_o_stretch.md`](phase_o_stretch.md) | Post-charter stretch (robustness, hexa composite, fork, PyPI) |
| [`phase_p_visibility.md`](phase_p_visibility.md) | Branded public site (GCE + Pages), feedback template, coupled fork v0.1 |
| [`GCE_VALIDATION.md`](GCE_VALIDATION.md) | Run full CI parity on a GCE VM (`gce_sync_vm.ps1`) |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | Release v0.5.0, visibility, fork, maintenance |

---

## Simulation domains

Six reference worlds share the same shock-schedule encoding but have different physics. They do not share state inside `step()`.

| Domain | `--mode` flag | Why this domain |
|--------|---------------|-----------------|
| Aggregate peg | `aggregate` | Stablecoin redemption panic |
| Network contagion | `network` | Panic spreading across a graph |
| Resource cascade | `resource_cascade` | [`WHY_RESOURCE_CASCADE.md`](WHY_RESOURCE_CASCADE.md) |
| Service backlog | `service_backlog` | [`WHY_SERVICE_BACKLOG.md`](WHY_SERVICE_BACKLOG.md) |
| Liquidity ladder | `liquidity_ladder` | [`WHY_LIQUIDITY_LADDER.md`](WHY_LIQUIDITY_LADDER.md) |
| Inventory buffer | `inventory_buffer` | [`WHY_INVENTORY_BUFFER.md`](WHY_INVENTORY_BUFFER.md) |

**Counterfactual cookbooks** (copy-paste CLI commands):

- [`aggregate_counterfactual_example.md`](aggregate_counterfactual_example.md)
- [`network_counterfactual_example.md`](network_counterfactual_example.md)
- [`resource_cascade_counterfactual_example.md`](resource_cascade_counterfactual_example.md)
- [`service_backlog_counterfactual_example.md`](service_backlog_counterfactual_example.md)
- [`liquidity_ladder_counterfactual_example.md`](liquidity_ladder_counterfactual_example.md)

**Mutation chain fixtures:** [`CHAIN_FIXTURES.md`](CHAIN_FIXTURES.md)

---

## Benchmarks and static viewers

| Document | What it covers |
|----------|----------------|
| [`../benchmarks/README.md`](../benchmarks/README.md) | Frozen bundle IDs, robustness sweeps, institutional composite |
| [`BUNDLED_ARTIFACTS.md`](BUNDLED_ARTIFACTS.md) | Checked-in JSON samples for viewers |

Serve the repo root over HTTP (`python -m http.server 8765`) to use the static viewers:

| Viewer | Path |
|--------|------|
| Replay timeline | [`../artifacts/replay_viewer/`](../artifacts/replay_viewer/) |
| Pareto front | [`../artifacts/pareto_viewer/`](../artifacts/pareto_viewer/) |
| Attribution / mutation chains | [`../artifacts/attribution_viewer/`](../artifacts/attribution_viewer/) |
| Institutional composite | [`../artifacts/composite_viewer/`](../artifacts/composite_viewer/) |

---

## Research policy

| Document | What it covers |
|----------|----------------|
| [`RESEARCH_FRONTIERS.md`](RESEARCH_FRONTIERS.md) | Ideas explicitly out of charter scope |
| [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md) | Coupled multi-kernel work belonging in a sibling repo |
| [`../ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) | Aspirational backlog (not binding until in `BOUNDARIES.md`) |

---

## Whitepaper

| Document | What it covers |
|----------|----------------|
| [`WHITEPAPER_INTRODUCTION.md`](WHITEPAPER_INTRODUCTION.md) | Conceptual overview — recommended entry point for external readers |
| [`WHITEPAPER.md`](WHITEPAPER.md) | Whitepaper hub with navigation table |
