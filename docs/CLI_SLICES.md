# CLI smoke slices (`tests/test_scripts_cli_smoke.py`)

Each **slice** is one subprocess test that runs a real CLI with small budgets and checks a schema or artifact field. This is the project’s guardrail for “script still works end-to-end” without a separate product UI.

**Count:** see `pytest tests/test_scripts_cli_smoke.py --collect-only -q` (currently **110+** tests; parametrized cases add more invocations).

**Related (not counted as slices here):**

- `tests/test_scripts_help_smoke.py` — every `scripts/*.py` exits 0 on `--help`
- Dedicated pins: `test_check_manifest_*.py`, `test_plot_institutional_composite.py`, `test_check_bundled_pareto_hypervolume.py`, …

---

## How to add a slice

1. Pick a **gap** (new flag, new mode, or script with no behavioral smoke).
2. Add `test_<script>_<behavior>_cli` at the bottom of `test_scripts_cli_smoke.py`.
3. Keep budgets tiny: `--generations 1`, `--horizon 8–14`, `--population-size 8–12`.
4. Assert **one** schema id or `simulation_mode` / `meta.cli` — not full golden metrics.
5. Run `python -m pytest tests/test_scripts_cli_smoke.py -q`.

---

## Slice groups (by theme)

| Group | Examples |
|-------|----------|
| **Core smoke** | `week1_smoke`, `fragility_surface`, `find_cheap_collapse`, `run_network_demo` |
| **Search** | `run_ga_demo`, `run_mc_demo` (all modes), domain GA demos, `run_coevolution`, `export_pareto_front` |
| **Replay export** | `export_replay` per mode, continue-after-collapse, neighbor JSON |
| **Counterfactuals** | `export_counterfactual` interventions per domain, chains, joint/triple merge |
| **Sweeps** | `counterfactual_epsilon_sweep`, `fragility_robustness_sweep` variants, `mechanism_design_policy_sweep` |
| **Benchmarks** | `run_benchmark_suite`, `benchmark_rollout`, manifest out/summary, `frozen_json_digest` |
| **Explain / narrate** | `export_explanation_dag`, `narrate_frozen_json`, `export_minimized_replay` + report |
| **Publication** | `plot_*`, `export_llm_narration_prompt` packs, `export_fragility_certificate`, `run_flagship_demo` |
| **Composite** | `institutional_composite_demo` (stdout + file, twin/triple/quad) |

---

## Scripts covered only via `--help` or other tests

| Script | Coverage |
|--------|----------|
| `check_manifest_digest.py` | `tests/test_check_manifest_digest.py` |
| `check_manifest_inventory.py` | `tests/test_check_manifest_inventory.py` |
| `check_manifest_summary.py` | `tests/test_check_manifest_summary.py` |
| `check_bundled_artifacts.py` | `tests/test_check_bundled_artifacts.py` |
| `check_flagship_bundled.py` | `tests/test_check_flagship_bundled.py` |
| `check_bundled_pareto_hypervolume.py` | `tests/test_bundled_pareto_hypervolume.py` |
| `validate_viewer_presets.py` | `tests/test_validate_viewer_presets.py` |
| `plot_institutional_composite_bars.py` | `tests/test_plot_institutional_composite.py` |
| `regenerate_bundled_viewer_samples.py` | Manual / maintainer (`docs/BUNDLED_ARTIFACTS.md`); too heavy for default CI slice |

---

## Roadmap vs slices

[`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) “exploration slices” are **product features** (schemas + CLIs + charter tests). This file tracks **CLI subprocess smokes** only. A phase can be **shipped** in `BOUNDARIES.md` while new smokes are still added here for regression.

There is **no** fixed list of exactly 100 roadmap slices to implement—**100** was the original CLI smoke target; the suite now exceeds that. Further work should target **uncovered behavior** (see table above), not inflate test count for its own sake.
