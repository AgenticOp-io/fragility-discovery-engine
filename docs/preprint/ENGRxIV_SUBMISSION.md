# engrXiv submission kit (FEL v0.1)

**Submit at:** https://engrxiv.org/about/submissions (Login / Register → make a submission)  
**Manuscript file:** `docs/preprint/FEL_preprint_v0.1.pdf` (rebuild after md edits: `python scripts/build_fel_preprint_pdf.py`)  
**Status:** PDF refreshed July 2026 for software 0.6.5 pointers — FEL semantics remain v0.1

## Checklist (engrXiv)

- [x] Legal right to submit (sole author; Agentic Ops)
- [x] PDF format
- [x] Relevant to engineering (simulation methodology / systems & software evidence contracts)
- [x] AI policy reviewed — see disclosure below ([AI policy](https://engrxiv.org/ai-policy))
- [x] Understand posting is permanent after acceptance

## Paste fields

### Title

```
Fragility Evidence Language (FEL): A Semantic Contract for Reproducible Stress-Search and Attribution in Discrete-Time Simulations
```

### Abstract

```
Simulation-based stress testing and adversarial search produce heterogeneous JSON artifacts—rollout replays, Pareto archives, counterfactual bundles, path traces, and audit certificates—whose metric deltas are easy to misread when sign conventions differ across export paths. We introduce the Fragility Evidence Language (FEL), a lightweight semantic contract that axiomatizes the types, evaluation laws, objective transforms, and attribution operators already implemented in the open-source Fragility Discovery Engine. FEL contributes three ideas: (1) a typed core eval(W, G, σ) → R separating worlds, exogenous shock schedules, and deterministic seeds; (2) dual attribution operators—Δ⁻ for counterfactual bundles (baseline minus variant) and Δ⁺ for forward path edges (successor minus predecessor)—with explicit roles so reviewers cannot conflate intervention effect with cumulative step increment; and (3) a versioned evidence constructor registry mapping schema IDs to merge graphs, explanation DAGs, fragility certificates, and institutional composites. FEL v0.1 is normative at the semantics layer; it does not define new physics or claim calibrated institutional risk. We describe the formal core, relate it to causal counterfactual framing and simulation reproducibility practice, walk through a flagship evidence chain, and state limitations honestly. A reference Python module encodes the operators for tests and tooling. FEL is intended as an interchange layer for discrete-time fragility experiments, not a replacement for domain-specific modeling languages.
```

### Keywords

```
simulation evidence, reproducibility, counterfactual attribution, Pareto search, stress testing, semantic contract, JSON schema, discrete-time simulation
```

### Suggested subjects (pick 1–2)

1. **Operations Research, Systems Engineering and Industrial Engineering** (primary)
2. **Electrical and Computer Engineering** (secondary — software/systems artifacts)
3. Other Engineering (fallback)

### Author

- **Name:** David Peterson  
- **Affiliation:** Agentic Ops  
- **ORCID:** *(add if you have one — helps moderation)*  
- **Email:** use the address on your engrXiv / ORCiD account  
- **URL:** https://agenticop.io  

### License

**CC BY 4.0** (matches Zenodo FEL snapshot and intended arXiv license)

### Related identifiers (comments / notes field if available)

- Software: https://github.com/AgenticOp-io/fragility-discovery-engine (tag `v0.6.5`)
- FEL semantics tag: `fel-v0.1.1`
- Zenodo FEL snapshot: https://doi.org/10.5281/zenodo.20455689
- Software concept DOI: https://doi.org/10.5281/zenodo.20455688 · v0.6.5: https://doi.org/10.5281/zenodo.21313024
- Live demo: https://fragility.agenticop.io/
- Spec: `docs/FRAGILITY_EVIDENCE_LANGUAGE.md` · module: `src/fragility_engine/fel/`

## AI disclosure (required — paste into comments or cover note)

engrXiv accepts AI-assisted drafting only with disclosure and human verification ([policy](https://engrxiv.org/ai-policy)).

```
AI disclosure: Prose drafting and structural editing used AI-assisted tools (Cursor / Composer) under human supervision. The author verified all definitions, operator signs, schema IDs, citations, and implementation claims against the open-source reference code (fragility_engine.fel), frozen benchmark suite, and the normative FEL spec. No fabricated data; no LLM as co-author; no unverified literature claims. Acceptable uses claimed: copy-editing/formatting and supervised pre-writing/organization (not verbatim unreviewed section generation).
```

This matches the Acknowledgments section already in the PDF.

## Why this should clear moderation (talking points)

- Not a “proposed framework” without output: reference implementation, CI goldens, PyPI package, Zenodo DOIs, public demo.
- Engineering contribution: semantic contract for reproducible stress-search evidence in discrete-time simulators (systems / OR / SE overlap).
- Honest non-claims: no calibrated institutional risk, no causal identifiability proofs.

## After acceptance

1. Copy the engrXiv DOI / URL into `docs/preprint/README.md`, `CITATION.cff` notes, and README cite block.
2. Update `docs/NEXT_STEPS.md` — mark engrXiv done (arXiv may remain blocked).
3. Optional: bump a docs-only note on the demo site via `gce_deploy_public_site.ps1`.

## If rejected

Appeal: director@engrxiv.org — emphasize reference implementation + frozen benchmarks + Zenodo archive. Parallel path remains Zenodo + WSC/PADS/ACM REP (see `PUBLISHING.md`).
