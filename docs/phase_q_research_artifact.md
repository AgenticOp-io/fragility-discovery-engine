# Phase Q — Research artifact polish

**Status:** proposed (not yet shipped)  
**Normative gates:** [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase Q)  
**Depends on:** Phases H–P shipped (artifact trail, FEL preprint, Zenodo, public workbench already exist)

## Purpose

Treat the project as a **citable research artifact**: paper + frozen evidence + open harness. Soften product-shaped overclaims, keep the six reference domains as **regression oracles / demos**, and make the citation path (preprint → Zenodo → certificate → BYOW pointer) the primary external story.

This phase does **not** invent new physics or search algorithms. It aligns positioning with what the code already is.

## Admission

1. Phase O/P complete on `main`.
2. No seventh reference-domain flight open.
3. Tracking issue per exit criterion below, each naming one acceptance check.

## In scope

- README / whitepaper intro lead with **harness + BYOW**, not “six institutional domains.”
- Soften “explain exactly why it broke” → counterfactual re-run / attribution language (match `BOUNDARIES.md` Phase D/I).
- Citation block: Zenodo DOI, `CITATION.cff`, FEL preprint PDF, `fel-v0.1.1` tag, certificate workflow.
- Optional JOSS / WSC / PADS / REP submission packaging checklist (docs only).
- Version consistency: `pyproject.toml`, `__init__.__version__`, release tags agree.
- Docs index: Phase Q memo linked from `docs/README.md`.

## Out of scope

- New reference worlds or charter domain slots.
- PyPI default publish (optional stretch; not required to close Q).
- CLI entry points (Phase R).
- Predicate / snapshot falsification harness (Phase S).
- Coupled mega-model on `main`.

## Exit criteria

- [ ] Root README “what this is / is not” paragraph matches `BOUNDARIES.md` non-goals; six domains labeled **toy regression oracles**.
- [ ] `docs/WHITEPAPER_INTRODUCTION.md` (or successor) no longer claims causal “exactly why”; points to counterfactual re-runs + FEL Δ conventions.
- [ ] Single **Cite** section: Zenodo DOI badge, BibTeX, certificate command, link to `docs/BRING_YOUR_OWN_WORLD.md`.
- [ ] `__init__.__version__` == `pyproject.toml` version == latest intended release tag policy documented in `RELEASING.md`.
- [ ] `docs/phase_q_research_artifact.md` (this file) linked from `docs/README.md` and `ROADMAP_NEXT.md`.
- [ ] Smoke: `python scripts/run_flagship_demo.py` still produces a certificate; Zenodo DOI resolves.

## Definition of done for PRs under Phase Q

- Docs-only or version-hygiene PRs preferred.
- No new `world/` modules.
- Any claim change must cite the matching non-goal in `BOUNDARIES.md`.
