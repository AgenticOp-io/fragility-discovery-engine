# Documentation index

This folder is the **user and operator guide** for the Fragility Discovery Engine. The root [`README.md`](../README.md) stays a short project overview; **start here** if you are installing, running CLIs, or reviewing artifacts.

Normative scope (what the project promises, phase gates, non-goals) lives in [`BOUNDARIES.md`](../BOUNDARIES.md). That file is law for contributors; this folder is law for **how to run and interpret** the software.

---

## Start here (by role)

| If you are… | Read first | Then |
|-------------|------------|------|
| **New developer** | [`HOW_TO_USE.md`](HOW_TO_USE.md) §2–4 | [`NEXT_STEPS.md`](NEXT_STEPS.md), run `bash scripts/ci_local.sh` |
| **Reviewer / paper appendix** | [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md) | [`benchmarks/README.md`](../benchmarks/README.md), [`BUNDLED_ARTIFACTS.md`](BUNDLED_ARTIFACTS.md) |
| **Platform / DevOps** | [`INSTALLATION.md`](INSTALLATION.md) | [`GCE_BOOTSTRAP.md`](GCE_BOOTSTRAP.md), [`GCE_DEPLOY_KEY.md`](GCE_DEPLOY_KEY.md) |
| **Architect / tech lead** | [`ARCHITECTURE.md`](ARCHITECTURE.md) | [`BOUNDARIES.md`](../BOUNDARIES.md), [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md) |
| **Looking up a flag or schema** | [`REFERENCE.md`](REFERENCE.md) | Script `--help`, tests under `tests/` |

---

## Core guides

| Document | Contents |
|----------|----------|
| [`HOW_TO_USE.md`](HOW_TO_USE.md) | Install, tutorials, viewers, artifact types, troubleshooting |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Packages, rollout pipeline, simulation modes, determinism |
| [`REFERENCE.md`](REFERENCE.md) | CLI matrix by mode, environment variables, JSON schemas |
| [`CLI_SLICES.md`](CLI_SLICES.md) | CLI subprocess smoke tests (slice inventory) |
| [`CLI_SLICES_BATCH3.md`](CLI_SLICES_BATCH3.md) | Ten-slice batch 3 (parity + bundled samples) |
| [`CLI_SLICES_BATCH4.md`](CLI_SLICES_BATCH4.md) | Ten-slice batch 4 (manifest floors + replay pairs) |
| [`CLI_SLICES_BATCH5.md`](CLI_SLICES_BATCH5.md) | Ten-slice batch 5 (charter + Phase N publication parity) |
| [`INSTALLATION.md`](INSTALLATION.md) | OS packages, Git credentials, CI parity scripts |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | Post-clone checklist and PR hygiene |
| [`PROJECT_STATUS.md`](PROJECT_STATUS.md) | Charter-scope completion snapshot (H–N + L) |
| [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md) | Complexity, parallelism, sweep cost, what not to claim |

---

## Reference domains (physics kernels)

Each domain is a **separate** `World` with the **same** shock-schedule encoding. They do not share state inside `step()`.

| Domain | `simulation_mode` | Narrative | Gate / checklist |
|--------|-------------------|-----------|------------------|
| Aggregate peg | `aggregate` | [`HOW_TO_USE.md`](HOW_TO_USE.md) §4.1 | Phase A–I in `BOUNDARIES.md` |
| Network contagion | `network` | — | Phase I network counterfactuals |
| Resource cascade | `resource_cascade` | [`WHY_RESOURCE_CASCADE.md`](WHY_RESOURCE_CASCADE.md) | [`phase_j_resource_cascade.md`](phase_j_resource_cascade.md) |
| Service backlog | `service_backlog` | [`WHY_SERVICE_BACKLOG.md`](WHY_SERVICE_BACKLOG.md) | [`phase_m_third_reference_domain.md`](phase_m_third_reference_domain.md) |
| Liquidity ladder | `liquidity_ladder` | [`WHY_LIQUIDITY_LADDER.md`](WHY_LIQUIDITY_LADDER.md) | [`phase_n_liquidity_ladder.md`](phase_n_liquidity_ladder.md) |

**Counterfactual cookbooks** (copy-paste commands): [`network_counterfactual_example.md`](network_counterfactual_example.md), [`aggregate_counterfactual_example.md`](aggregate_counterfactual_example.md), [`resource_cascade_counterfactual_example.md`](resource_cascade_counterfactual_example.md), [`service_backlog_counterfactual_example.md`](service_backlog_counterfactual_example.md), [`liquidity_ladder_counterfactual_example.md`](liquidity_ladder_counterfactual_example.md).

**Mutation chain fixtures:** [`CHAIN_FIXTURES.md`](CHAIN_FIXTURES.md).

---

## Benchmarks, artifacts, publication

| Document | Contents |
|----------|----------|
| [`../benchmarks/README.md`](../benchmarks/README.md) | Frozen bundle IDs, robustness sweeps, institutional composite |
| [`BUNDLED_ARTIFACTS.md`](BUNDLED_ARTIFACTS.md) | Checked-in JSON for viewers and CI pins |
| [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md) | One end-to-end reviewer path |
| [`phase_l_publication.md`](phase_l_publication.md) | Narration, plots, LLM prompt packs |
| [`WHITEPAPER.md`](WHITEPAPER.md) | Long-form technical narrative |
| [`WHITEPAPER_INTRODUCTION.md`](WHITEPAPER_INTRODUCTION.md) | Short intro for external readers |

---

## Research policy (not shipped product)

| Document | Contents |
|----------|----------|
| [`RESEARCH_FRONTIERS.md`](RESEARCH_FRONTIERS.md) | Ideas explicitly out of charter |
| [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md) | Coupled multi-kernel work in a sibling repo |
| [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) | Aspirational backlog (not binding until in `BOUNDARIES.md`) |

---

## Static viewers (browser)

Serve the **repository root** over HTTP (`python -m http.server 8765`), then open:

| Viewer | Path | Accepts |
|--------|------|---------|
| Replay timeline | [`../artifacts/replay_viewer/`](../artifacts/replay_viewer/) | Replay JSON from `rollout_to_replay_dict` |
| Pareto | [`../artifacts/pareto_viewer/`](../artifacts/pareto_viewer/) | `pareto-front-v1` |
| Attribution | [`../artifacts/attribution_viewer/`](../artifacts/attribution_viewer/) | Merges and mutation-chain path traces |
| Composite | [`../artifacts/composite_viewer/`](../artifacts/composite_viewer/) | Institutional composite v1–v3 |

Each viewer folder has its own `README.md` describing JSON contracts.

---

## What “Phase” means

**Phase** labels (H, I, J, L, M, N, …) are **charter section names** in [`BOUNDARIES.md`](../BOUNDARIES.md). They record how features were gated and tested. They are **not** separate products, licenses, or install tiers. Shipped code may span many phases; read exit criteria in `BOUNDARIES.md` for what is actually required in CI.
