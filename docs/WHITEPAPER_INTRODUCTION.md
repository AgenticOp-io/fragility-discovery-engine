# Fragility Discovery Engine — Introduction Whitepaper

**Purpose:** A concise overview for researchers, engineers, and program leads who work on **stress testing**, **scenario analysis**, **search over simulations**, **network contagion**, **resilience drills**, or **traceable explanation outputs**.

**Repository:** [github.com/theorem6/fragility-discovery-engine](https://github.com/theorem6/fragility-discovery-engine)  
**Primary contact channel:** [GitHub Issues](https://github.com/theorem6/fragility-discovery-engine/issues) on that repository (best for technical questions, collaboration, and reproducibility reports).

---

## 1. Executive summary

The **Fragility Discovery Engine** is an open-source Python stack built for **repeatable runs** (fixed seeds): it **searches** over **shock schedules** (Monte Carlo, genetic algorithms, co-evolution) in several **reference simulation models** (aggregate peg, network contagion, resource cascade, service backlog—each **separate**, not coupled), **maximizes stated instability metrics**, and writes **JSON outputs** you can archive and cite: replay traces, **small failing schedules**, **counterfactual** and **step-wise sensitivity (mutation-chain)** comparisons, **Pareto** tradeoff sets, and an optional **`fragility-certificate-v1`** digest of files and environment.

It is **not** a live trading system, a blockchain product, or a calibrated forecast of real institutions. It is a **research tool** for controlled fragility analysis with **versioned JSON schemas** and **frozen benchmark checks** (`fragility_engine.benchmarks.suite`, CI)—aimed at teams who want **clear, reproducible records** instead of slides-only summaries.

---

### Terminology (plain language)

| Common industry / research term | How it shows up here |
|-----------------------------------|----------------------|
| **Stress testing**, **scenario analysis** | Search and evaluation over **exogenous shock schedules** (same schedule encoding across reference worlds). |
| **Sensitivity analysis** | Scalar **ε-sweeps** and one-axis counterfactuals with other parameters pinned. |
| **Directed search** (related to fuzzing ideas) | Monte Carlo and **genetic algorithms (GA)** over schedules (same inputs + seeds ⇒ same outputs). |
| **Multi-objective analysis** | **Pareto** sets trading instability against **attack cost** (and related scalars). |
| **Explainability / attribution** (narrow) | **Rule-based** interventions (e.g. remove shocks, change reset numbers, edit edges)—not neural “feature importance”. |
| **Audit trail**, **provenance** | Schema-versioned JSON plus optional **`fragility-certificate-v1`** digests. |
| **Regression testing** | **Frozen** benchmark rows in CI (`fragility_engine.benchmarks.suite`, `pytest`; charter **Phase H** in [`BOUNDARIES.md`](../BOUNDARIES.md)). |

## 2. Problem framing

Across several communities, the same pattern appears: high-stakes systems are judged under **scenario stress** or **robustness testing**, but **traces** of *why* a run failed—what shocks, in what order, at what minimal sufficiency—are often informal slides or ad-hoc notebooks. That weakens **auditability**, **comparison across methods**, and **handoff** between modeling and assurance.

Recent research underscores demand for:

- **Robustness and fragility under stress** in learning and control (e.g. parameter and policy behavior under adversarial or distributional stress in RL safety literature).
- **Standardized, reproducible evaluation** of post-hoc and counterfactual-style explanations (benchmark suites in the XAI / recourse literature emphasize fidelity, stability, and comparable protocols).

This repository is one **codebase** where search, metrics, minimization, counterfactuals, light narration helpers, and **benchmark manifests** all use the same rollout contract—so a failure case is **frozen JSON** you can compare across runs, not a one-off plot.

---

## 3. What the software does (capabilities)

| Layer | Role |
|--------|------|
| **World** | Domain physics only; no hidden “attack hooks” inside `World.step`. |
| **Agents** | Thin archetypes: observe → decide → act. |
| **Adversary** | **Search** over shock schedules: Monte Carlo, GA, and extensions (deterministic given seeds). |
| **Explain** | Ablation, minimization, counterfactual bundles, mutation chains, path traces, joint merges, narration helpers. |
| **Network** | Contagion on explicit graphs (`ContagionGraph`), neighbor-list–friendly updates. |
| **Coevolution** | Alternating attacker/defender search; **Pareto** output for two-objective trade-offs. |

**Domains shipped as reference kernels** (same shock-schedule encoding; different physics): aggregate **stablecoin peg** toy, **graph contagion** (`StablecoinNetworkWorld`), **resource cascade** (`ResourceCascadeWorld`; charter section **Phase J** in [`BOUNDARIES.md`](../BOUNDARIES.md)), and **service backlog / latency stress** (`ServiceBacklogWorld`; charter section **Phase M**, `simulation_mode` **`service_backlog`**). Each domain documents explicit **non-goals** (see also [`WHY_RESOURCE_CASCADE.md`](WHY_RESOURCE_CASCADE.md), [`WHY_SERVICE_BACKLOG.md`](WHY_SERVICE_BACKLOG.md)) so scope does not drift into generic “digital twin” platforms.

**Decoupled audit composites** bundle one attacker schedule across multiple kernels **without** cross-`World` coupling inside `step()`: `fragility-institutional-composite-v1` (network + cascade), **v2** (+ aggregate peg), **v3** (+ service backlog). CLI: `scripts/institutional_composite_demo.py` (`--triple`, `--quad`).

**Explanation outputs** include **minimal-collapse** reports, **counterfactual** bundles (`remove_steps`, scalar shifts, network patches), **ordered mutation chains** with optional **path traces** (network, resource cascade, service backlog), **merged attribution graphs** (`attribution-merge-v1`), **ε-sweeps** with trace export, and **explanation DAGs** built from data, not LLM prose. Cookbooks: [`network_counterfactual_example.md`](network_counterfactual_example.md), [`resource_cascade_counterfactual_example.md`](resource_cascade_counterfactual_example.md), [`service_backlog_counterfactual_example.md`](service_backlog_counterfactual_example.md).

**Reproducibility:** fixed RNG seeds, CI workflows, Phase **H** golden bundles (`scripts/run_benchmark_suite.py --validate`), flagship demo (`scripts/run_flagship_demo.py`), ensemble / mechanism-design / robustness sweep CLIs (see [`benchmarks/README.md`](../benchmarks/README.md)), and **`fragility-certificate-v1`** (`scripts/export_fragility_certificate.py`). Pareto and replay JSON use schema-versioned contracts (see [`HOW_TO_USE.md`](HOW_TO_USE.md)).

---

## 4. Who the natural audiences are

These segments map to **public** research and engineering communities (venues, working papers, open benchmarks)—not to any endorsement by those organizations.

### 4.1 Robustness, distribution shift, and strategic behavior (ML)

Teams working on **adversarial robustness**, **distribution shift**, **strategic users**, or **reliable ML under imperfect data** often need **toy worlds** where attacks and metrics are explicit. NeurIPS-style **workshops** that publish calls for papers and non-archival tracks are a natural fit for **benchmark or systems** contributions derived from this repo.

**Example venue (illustrative):** reliability / robustness workshops in the NeurIPS ecosystem (topics often include adversarial stress, strategic behavior, and benchmarks; follow the **current** workshop site and call for papers rather than this link alone).

### 4.2 Counterfactual explanations, recourse, and XAI benchmarks

Groups comparing **counterfactual explanations**, **algorithmic recourse**, or **faithfulness / stability** metrics benefit from **another controlled simulator** where ground-truth interventions are **mechanical** (shock schedules, topology, thresholds), not buried inside a proprietary model API. Adjacent benchmark traditions (e.g. libraries and surveys for counterfactual **recourse** and **open XAI** evaluation) are useful **conceptual peers**, not competitors.

### 4.3 Financial stability and stress-testing methodology (research, not trading)

Central banks, the IMF, and academic macro-finance produce **stress-testing** and **contagion** methodology (e.g. macro-prudential and multi-scenario frameworks). This repository’s **peg toy** is a **deliberately simplified** pedagogical kernel: appropriate for **methodology dialogue** and **toy validation** of search-and-explain pipelines, **not** for institution-specific calibration or policy claims. Outreach should be framed as **open science / tooling**, not governance-grade forecasting.

### 4.4 RL and safety-critical simulation labs

Reinforcement learning and **safe RL** research increasingly stress **robustness** and **viability under perturbations**. Labs that already run **custom simulators** for assurance can embed or compare against this engine’s **artifact contracts** (replay JSON, Pareto JSON, certificate) rather than re-deriving export schemas.

### 4.5 Internal platform / red-team engineering

Product security and resilience teams sometimes need **repeatable** “find a small failing schedule” loops with **exportable evidence**. The CLI-first design matches **CI and audit** expectations; any future UI should remain a thin wrapper over the same APIs (per project boundaries).

---

## 5. How to evaluate the project quickly

1. **Read boundaries:** [`BOUNDARIES.md`](../BOUNDARIES.md) — non-goals and phase gates.  
2. **Run tests:** `python -m pytest` after `pip install -e ".[dev]"` (portable; `pytest.exe` is Windows-venv-only).  
3. **Validate benchmarks:** `python scripts/run_benchmark_suite.py --validate` (see [`benchmarks/README.md`](../benchmarks/README.md)).  
4. **Reviewer path:** [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md).  
5. **Honest scale:** [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md).  
6. **Service backlog domain checklist:** [`phase_m_third_reference_domain.md`](phase_m_third_reference_domain.md).  
7. **One-shot bundle:** `python scripts/run_flagship_demo.py` (see README for defaults and output layout).

---

## 6. Outreach routing (public channels — not cold personal spam)

Use **institutional or venue** entry points so messages reach the right desk. **Do not** infer private e-mail addresses from this document; use official directories.

| Audience | Suggested routing |
|----------|-------------------|
| **Workshop / conference chairs** | Official workshop site → OpenReview group or listed organizers → **university or lab pages** linked from those profiles. |
| **Open-source collaborators** | [GitHub Issues](https://github.com/theorem6/fragility-discovery-engine/issues) with a minimal repro, seed, and artifact JSON if applicable. |
| **Policy / macro stress-test research (high level)** | Publications portals (e.g. IMF working papers, ECB working papers, Fed research) — engage as **readers/citers** first; direct partnership requires institutional process. |
| **Corporate research labs** | Public research blog contact or **open positions** pages; reference this repo as an **artifact** for exploratory collaboration. |

---

## 7. Positioning statement (safe to paste into an e-mail)

> We are sharing the **Fragility Discovery Engine** ([github.com/theorem6/fragility-discovery-engine](https://github.com/theorem6/fragility-discovery-engine)), an open-source **deterministic** simulation stack for **stress-style exploration** of shock schedules, clear **fragility metrics**, **small failing scenarios**, and **counterfactual** JSON exports—with **benchmark checks** and a **`fragility-certificate-v1`** path for file digests. It is **not** a production market or policy model; it is a **research tool** for careful comparisons. We welcome pointers to **workshops, benchmarks, or teams** where a **command-line, JSON-first** workflow fits.

---

## 8. References (external, illustrative)

- Kpotufe et al., *Fragile, Robust, and Antifragile: A Perspective from Parameter Responses in Reinforcement Learning Under Stress* — [arXiv:2506.23036](https://arxiv.org/abs/2506.23036) (fragility / robustness framing in RL).  
- IMF, *Macro-Prudential Stress Test Models: A Survey* — [IMF publications](https://www.imf.org/en/publications/wp/issues/2023/08/25/macro-prudential-stress-test-models-a-survey-537990) (macro stress-test context; **not** implied calibration to this toy).  
- Workshop example: reliability / robustness workshops (see current NeurIPS / ICML workshop lists for URLs and chairs).  
- XAI benchmarking (for **comparison norms**, not runtime dependencies): e.g. OpenXAI, CARLA recourse libraries — look up current URLs and citation keys when writing related work.

---

## 9. Document control

| Field | Value |
|--------|--------|
| **Version** | 1.4 |
| **Last updated** | 2026-05 — terminology table + benchmark wording aligned with `BOUNDARIES` |
| **Repo state** | Tracks `main`; cite commit when forwarding alongside frozen JSON. |
| **Maintainer path** | Prefer **GitHub Issues** for accuracy and public record. |

---

*End of introduction whitepaper.*
