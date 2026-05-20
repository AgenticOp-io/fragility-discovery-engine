# Phase O — post-charter stretch (shipped)

Charter phases **H–N** and **L** remain complete. Phase **O** adds optional tooling without coupled physics on `main`.

## Shipped slices

| Slice | Entry point |
|-------|-------------|
| Sixth domain (`inventory_buffer`) | `scripts/run_inventory_buffer_ga_demo.py`, `--mode inventory_buffer` on `export_replay.py` |
| Frozen bundle | `inventory_buffer_rollout_v1` in `run_benchmark_suite.py --validate` |
| Hexa composite | `scripts/institutional_composite_demo.py --hexa` → schema **v5** |
| Robustness stretch | `scripts/fragility_robustness_stretch.py --preset small\|medium\|large` |
| Mechanism lattice | `scripts/mechanism_design_policy_sweep.py --defender-strength-lattice 0.2,0.5,0.8` |
| Local dashboard | `scripts/export_static_dashboard.py` |
| Coupled fork | `forks/coupled_institution/` |
| PyPI | `.github/workflows/pypi.yml` (manual dispatch) |

## Non-goals (still)

Hosted SaaS, production market/policy models, coupled `World.step()` on `main`.
