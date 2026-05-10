# Fragility Discovery Engine — Introduction Whitepaper

**Purpose:** A short, forwardable overview for researchers, engineers, and program leads who evaluate **stress testing**, **adversarial / coverage-guided search**, **network contagion**, or **reproducible explanation artifacts** in simulation.

**Repository:** [github.com/theorem6/fragility-discovery-engine](https://github.com/theorem6/fragility-discovery-engine)  
**Primary contact channel:** [GitHub Issues](https://github.com/theorem6/fragility-discovery-engine/issues) on that repository (best for technical questions, collaboration, and reproducibility reports).

---

## 1. Executive summary

The **Fragility Discovery Engine** is an open-source, **deterministic-first** Python stack that **searches** for exogenous shock schedules (Monte Carlo, genetic algorithms, coevolutionary loops) over **modular worlds**, **maximizes explicit instability metrics**, then produces **reviewer-grade artifacts**: frozen replay JSON, greedy **minimal collapse sequences**, **counterfactual** and **mutation-chain** explanations, **Pareto fronts**, and a **`fragility-certificate-v1`** bundle for digests and environment fingerprints.

It is **not** a live trading system, a blockchain product, or a calibrated forecast of real institutions. It is a **laboratory** for disciplined fragility analysis with **schema-versioned exports** and **Phase H** benchmark validation hooks—aimed at teams who care about **evidence before chrome** and **reproducible narratives** over dashboards alone.

---

## 2. Problem framing

Across several communities, the same pattern appears: high-stakes systems are judged under **scenario stress** or **robustness testing**, but **traces** of *why* a run failed—what shocks, in what order, at what minimal sufficiency—are often informal slides or ad-hoc notebooks. That weakens **auditability**, **comparison across methods**, and **handoff** between modeling and assurance.

Recent research underscores demand for:

- **Robustness and fragility under stress** in learning and control (e.g. parameter and policy behavior under adversarial or distributional stress in RL safety literature).
- **Standardized, reproducible evaluation** of post-hoc and counterfactual-style explanations (benchmark suites in the XAI / recourse literature emphasize fidelity, stability, and comparable protocols).

This engine attacks the **systems layer**: a **single codebase** where search, metrics, minimization, counterfactuals, narration helpers, and **benchmark manifests** share one rollout contract—so a collapse story is **frozen JSON**, not a one-off plot.

---

## 3. What the software does (capabilities)

| Layer | Role |
|--------|------|
| **World** | Domain physics only; no hidden “attack hooks” inside `World.step`. |
| **Agents** | Thin archetypes: observe → decide → act. |
| **Adversary** | Deterministic search over shock schedules (MC, GA, cost-penalized variants). |
| **Explain** | Ablation, minimization, counterfactual bundles, optional path traces. |
| **Network** | Contagion on explicit graphs (`ContagionGraph`), neighbor-list–friendly updates. |
| **Coevolution** | Alternating attacker/defender search; Pareto export for tradeoff narratives. |

**Domains in flight** include an aggregate **stablecoin peg toy** (reference domain), **graph contagion**, and a **resource cascade** scaffold—each with explicit **non-goals** in project documentation so scope does not drift into generic “digital twin” platforms.

**Reproducibility:** fixed RNG seeds, CI workflows, Phase **H** golden bundles (`scripts/run_benchmark_suite.py --validate`), flagship demo (`scripts/run_flagship_demo.py`), and **`fragility-certificate-v1`** (`scripts/export_fragility_certificate.py`).

---

## 4. Who the natural audiences are

These segments map to **public** research and engineering communities (venues, working papers, open benchmarks)—not to any endorsement by those organizations.

### 4.1 Robustness, distribution shift, and strategic behavior (ML)

Teams working on **adversarial robustness**, **distribution shift**, **strategic users**, or **reliable ML under imperfect data** often need **toy worlds** where attacks and metrics are explicit. NeurIPS-style **workshops** that publish calls for papers and non-archival tracks are a natural fit for **benchmark or systems** contributions derived from this repo.

**Example venue (illustrative):** [Reliable ML from Unreliable Data — NeurIPS 2025 Workshop](https://reliablemlworkshop.github.io/) — topics include adversarial robustness, strategic behavior in socio-technical systems, and benchmarks; submissions historically via OpenReview (see workshop site for the current group link and organizers).

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
2. **Run tests:** `pytest` after `pip install -e ".[dev]"`.  
3. **Validate benchmarks:** `python scripts/run_benchmark_suite.py --validate` (see [`benchmarks/README.md`](../benchmarks/README.md)).  
4. **Reviewer path:** [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md).  
5. **Honest scale:** [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md).  
6. **One-shot bundle:** `python scripts/run_flagship_demo.py` (see README for defaults and output layout).

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

> We are sharing the **Fragility Discovery Engine** ([github.com/theorem6/fragility-discovery-engine](https://github.com/theorem6/fragility-discovery-engine)), an open-source **deterministic** simulation and search stack for **shock schedules**, **collapse metrics**, **minimal replays**, and **counterfactual** exports—with **benchmark validation** and a **`fragility-certificate-v1`** path for reproducible digests. It is explicitly **not** a production market or policy model; it is a **laboratory** for rigorous fragility narratives and comparable artifacts. We would welcome pointers to **venues, benchmarks, or teams** where a **CLI-first, schema-versioned** stress-and-explain loop would be on-scope.

---

## 8. References (external, illustrative)

- Kpotufe et al., *Fragile, Robust, and Antifragile: A Perspective from Parameter Responses in Reinforcement Learning Under Stress* — [arXiv:2506.23036](https://arxiv.org/abs/2506.23036) (fragility / robustness framing in RL).  
- IMF, *Macro-Prudential Stress Test Models: A Survey* — [IMF publications](https://www.imf.org/en/publications/wp/issues/2023/08/25/macro-prudential-stress-test-models-a-survey-537990) (macro stress-test context; **not** implied calibration to this toy).  
- Workshop example: [Reliable ML from Unreliable Data @ NeurIPS 2025](https://reliablemlworkshop.github.io/) (robustness / strategic behavior / benchmarks).  
- XAI benchmarking landscape (peers for **evaluation culture**, not code dependencies): e.g. OpenXAI, CARLA recourse library — search for current URLs and citation keys when writing formal related work.

---

## 9. Document control

| Field | Value |
|--------|--------|
| **Version** | 1.0 |
| **Repo state** | Tracks `main`; cite commit when forwarding alongside frozen JSON. |
| **Maintainer path** | Prefer **GitHub Issues** for accuracy and public record. |

---

*End of introduction whitepaper.*
