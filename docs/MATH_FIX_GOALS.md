# Math fix goals

Audit date: 2026-05-29. Source: Pareto/hypervolume semantic review and literature cross-check (Zitzler & Thiele hypervolume, Deb dominance, DeGroot diffusion, Holland GA).

## Goal 1 — Align hypervolume with attack Pareto semantics (critical)

**Problem:** `pareto_indices` maximizes severity and minimizes attack cost, but CI hypervolume used `nondominated_points_min` on raw `(severity, attack_cost)` — treating lower severity as better. That measures a different front than the search archive.

**Fix:** Map attack trade-offs to minimization coordinates `(-severity, attack_cost)` before non-dominated filtering and hypervolume. Add `hypervolume_2d_attack_pareto` and shared reference-point helpers in `benchmarks/hypervolume.py`.

**Acceptance:** Non-dominated count on transformed points matches `pareto_indices` on bundled samples; all hypervolume pin tests pass with regenerated fixtures.

## Goal 2 — Regenerate pinned hypervolume fixtures

**Problem:** Bundled Pareto pins, coupled-fork Pareto pins, and flagship bundled HV were computed with the wrong objective directions.

**Fix:** Update check scripts to use attack-Pareto hypervolume; regenerate:

- `tests/fixtures/benchmarks/bundled_pareto_hypervolume_pins.json`
- `tests/fixtures/benchmarks/coupled_fork_pareto_search_pins.json`
- `tests/fixtures/benchmarks/coupled_fork_pareto_search_v2_pins.json`
- Flagship `meta.hypervolume_policy` and expected HV in tests

**Acceptance:** `check_bundled_pareto_hypervolume.py`, `check_coupled_fork_pareto.py`, `check_flagship_bundled.py`, and related pytest modules green.

## Goal 3 — Document math conventions fully

**Problem:** Objective directions, delta sign conventions, and toy-model scope are scattered across `ALGORITHMS.md`, code comments, and the audit notes.

**Fix:** Add `docs/MATH.md` as the canonical math reference: objectives, dominance, hypervolume transform, GA operators, world update equations, counterfactual deltas, co-evolution signs, and explicit non-goals (not calibrated economics).

**Acceptance:** Public site renders `/docs/math.html`; `ALGORITHMS.md` and `HOW_TO_USE.md` link to it.

## Goal 4 — Clarify generic vs attack hypervolume in tests

**Problem:** `pinned_pareto_front_minimal.json` uses generic 2-D minimization points to test the sweep algorithm — not attack archive storage format.

**Fix:** Update fixture descriptions and add a test that attack-transform ND matches `pareto_indices`.

**Acceptance:** No ambiguity between algorithm regression fixtures and attack-Pareto CI pins.

## Out of scope (document only, no code change)

- Coupled fork Gaussian step noise (research fork; documented in `MATH.md`)
- Counterfactual vs mutation-chain delta sign differences (documented, not unified)
- Replacing scalar GA with NSGA-II (charter: post-hoc Pareto archive only)

## Done when

- [x] Goals 1–4 implemented
- [x] `python -m pytest tests/test_hypervolume.py tests/test_bundled_pareto_hypervolume.py tests/test_flagship_bundled.py tests/test_attack_pareto_hypervolume.py -q` passes
- [x] `python scripts/check_bundled_pareto_hypervolume.py` passes
- [x] `python scripts/check_coupled_fork_pareto.py` passes
- [ ] Changes pushed to `main`
