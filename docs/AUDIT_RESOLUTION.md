# Audit resolution log

Tracks findings from the **2026 project audit** (repo substance review) and the **2026-05-29 math soundness audit** (`MATH_FIX_GOALS.md`). Use this before publishing (arXiv, open source, preprint).

---

## Project audit (architecture / docs)

| Severity | Concern | Resolution | Status |
|----------|---------|------------|--------|
| High | Docs drift after Phase N/O — roadmap still read as draft | `ROADMAP_NEXT.md` Phase N marked **shipped**; removed draft gate language; `benchmarks/README.md` lists all frozen bundles | Fixed |
| Medium | Entry docs under-list `liquidity_ladder` / `inventory_buffer` | `README.md` Phase O narrative; `export_replay` / `benchmark_rollout` rows include all six `--mode` values; `HOW_TO_USE.md` already complete | Fixed |
| Medium | Toy domains read as real institutional models | `WHITEPAPER_INTRODUCTION.md`, `MATH.md` §1, `BOUNDARIES.md` non-goals; this file states scope explicitly | Documented |
| Medium | Some tests are smoke-only | Added `counterfactual-bundle-v1` schema on all counterfactual exports; `check_bundled_artifacts.py` validates JSON schema identity | Fixed |
| Low | No `console_scripts` entry points | Deferred — scripts remain `python scripts/…`; document in `HOW_TO_USE.md` | Open (optional) |
| — | `export_replay.py` missing domains | Already supports all six modes including `liquidity_ladder` and `inventory_buffer` | N/A (was fixed) |

**Verdict unchanged:** worthwhile as a **deterministic research harness** and reproducibility pipeline — not a calibrated institutional risk engine.

---

## Math audit (2026-05-29)

| Goal | Issue | Resolution | Status |
|------|-------|------------|--------|
| 1 | Hypervolume used wrong objective directions | `hypervolume_2d_attack_pareto` + `(-severity, cost)` transform | Done |
| 2 | Stale hypervolume pins | Regenerated bundled / coupled-fork / flagship pins | Done |
| 3 | Scattered math conventions | `docs/MATH.md` canonical; FEL v0.1 for evidence semantics | Done |
| 4 | Generic vs attack HV confusion | `test_attack_pareto_hypervolume.py`; fixture comments in `MATH.md` §4.1 | Done |

**Out of scope (documented, not bugs):**

- Coupled fork Gaussian noise — `MATH.md` §9
- Δ⁻ vs Δ⁺ attribution roles — `FRAGILITY_EVIDENCE_LANGUAGE.md` / FEL
- NSGA-II — charter uses post-hoc Pareto archive only

**Goal 3 acceptance update:** `MATH.md` is **repo-only** (not on the public product site). Public docs link to **FEL** (`/docs/fel.html`) for formal evidence semantics.

---

## Publish / open-source checklist

- [x] Math hypervolume semantics aligned with `pareto_indices`
- [x] FEL documents dual attribution operators
- [x] Preprint author attribution (David Peterson, Agentic Ops)
- [x] `LICENSE` (Apache 2.0) in repo root
- [ ] arXiv upload (optional; requires endorser or qualifying account)
- [ ] Zenodo DOI on release tag (optional)

---

## Verification commands

```powershell
python -m pytest tests/test_attack_pareto_hypervolume.py tests/test_hypervolume.py -q
python scripts/check_bundled_pareto_hypervolume.py
python scripts/check_bundled_artifacts.py
powershell -File scripts/ci_local.ps1
```

Last verified: update date when CI is green after your changes.
