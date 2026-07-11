# Where to publish the FEL paper

This note ranks venues for **Fragility Evidence Language (FEL) v0.1** — a *semantic contract* paper, not a new physics or ML model paper. Match the venue to that framing.

---

## Recommended path (practical)

### 1. Preprint first (do this regardless)

**Preferred discovery stamp:** [engrXiv](https://engrxiv.org/) (Engineering Archive) — no arXiv-style endorsement. Paste kit: [`ENGRxIV_SUBMISSION.md`](ENGRxIV_SUBMISSION.md).

**Also keep:** Zenodo DOI [10.5281/zenodo.20455689](https://doi.org/10.5281/zenodo.20455689) (`fel-v0.1.1`) as the archival record.

**arXiv (optional):** `cs.SE` primary — blocked on endorsement until someone vouchsafes a first-time poster; pack in [`ARXIV_ENDORSEMENT.md`](ARXIV_ENDORSEMENT.md).

**Why:** Establishes priority, is citable immediately, aligns with open-source release. Link the GitHub repo, frozen benchmark digest, and `fel-v0.1.1` tag in the abstract / notes.

**Timeline:** Same week as (or day before) any conference submission.

---

### 2. Best fit conferences (pick one target)


| Venue                                                                                       | Fit               | Notes                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[Winter Simulation Conference (WSC)](https://www.wintersim.org/)**                        | **Strongest**     | Discrete-event / discrete-time simulation community; methodology and reproducibility papers are normal. Frame FEL as an *evidence interchange layer* for stress-search experiments. |
| **[SIGSIM PADS](https://sigsim.org/PADS)** (ACM Principles of Advanced Discrete Simulation) | **Strong**        | Shorter, tighter than WSC; good for formal semantics + reference implementation. Often co-located with SIGSIM conferences.                                                          |
| **[ICSE NIER](https://conf.researchr.org/home/icse-2026)** (New Ideas and Emerging Results) | **Good**          | If you stress schema contracts, CI golden pins, and “evidence before chrome.” 4-page format; less simulation audience, more SE reproducibility.                                     |
| **[ASE](https://conf.researchr.org/home/ase)** (tool/demo or short paper tracks)            | **Good**          | If you demo the JSON artifact graph + `fragility_engine.fel` reference module as an engineering artifact.                                                                           |
| **[ACM REP](https://rep-workshop.github.io/)** (Reproducibility workshop)                   | **Good workshop** | Narrow but perfect audience; pair with flagship certificate + manifest digest workflow.                                                                                             |


**Avoid overselling:** Do not submit to venues expecting novel algorithms, calibrated finance, or regulatory stress-test certification — the project charter explicitly disclaims those (`BOUNDARIES.md`).

---

### 3. Journal options (after arXiv + one conference cycle)


| Journal                                                                                                  | Fit                                                                                                                                                                    |
| -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[Software: Practice and Experience](https://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1097-024X)** | Reference implementation + semantic spec + case study; familiar with open-source systems papers.                                                                       |
| **[Journal of Simulation (OR Society)](https://www.tandfonline.com/journals/tjsm20)**                    | Simulation methodology; FEL as contract for adversarial search experiments.                                                                                            |
| **[Empirical Software Engineering](https://www.springer.com/journal/10664)**                             | If you add an empirical study (e.g. mis-read deltas before/after FEL naming in user tests). Heavier lift.                                                              |
| **[Journal of Open Source Software (JOSS)](https://joss.theoj.org/)**                                    | **Not a substitute** for this paper — JOSS is a 1-page software paper. Submit JOSS *in parallel* for the engine; keep FEL as the conceptual preprint/conference paper. |


---

## What *not* to prioritize (unless you change the paper)


| Venue type                      | Why lower priority                                                                  |
| ------------------------------- | ----------------------------------------------------------------------------------- |
| NeurIPS / ICML main             | FEL is not a learning method; workshop XAI only if you add ML baseline comparisons. |
| Top finance / risk journals     | Reviewers will expect calibration and regulatory mapping you explicitly reject.     |
| Pure formal methods (CAV, LICS) | No temporal logic or verification proof — semantics are operational, not deductive. |


---

## Submission packaging checklist

1. **One sentence contribution** — “FEL names the evidence operators already produced by fragility search so counterfactual and path attributions cannot be confused.”
2. **Artifact appendix** — `python scripts/run_flagship_demo.py` → certificate JSON; cite schema IDs from `fel.SCHEMA_REGISTRY`.
3. **Honest limitations box** — toy worlds, no Shapley guarantees, Δ operators are conventions not causal identifiability proofs.
4. **Open access** — repository + preprint + (optional) Zenodo DOI on release tag for long-term archiving.
5. **Dual submission policy** — arXiv + conference is usually fine; check specific CFP for “prior public dissemination” rules (ICSE allows arXiv).

---

## Suggested timeline


| Month        | Action                                                                                                        |
| ------------ | ------------------------------------------------------------------------------------------------------------- |
| Now          | Post arXiv preprint; add badge + citation to repo README                                                      |
| +2–4 weeks   | Submit WSC or PADS short paper (check deadline — WSC typically ~March for December conference)                |
| +3 months    | Revise from reviews; extend with user study or `.fel` parser if reviewers ask for “language” beyond semantics |
| +6–12 months | Journal extension (SPE or Journal of Simulation) with benchmark suite evaluation section                      |


---

## Authoring contacts (optional communities)

- **SIGSIM** mailing list / Discord — simulation researchers building reproducible experiment contracts.
- **Reproducibility workshops** at ICSE/ASE — evidence schema papers.
- **Causal inference** — cite Pearl for counterfactual *framing* only; do not claim FEL solves identifiability.

For questions on this repo’s charter constraints before submitting, re-read `[BOUNDARIES.md](../../BOUNDARIES.md)` § Explicit non-goals.