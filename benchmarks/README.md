# Phase H benchmark bundles

This folder documents **frozen deterministic bundles** implemented in code:

- `fragility_engine.benchmarks.suite` — four bundles (`aggregate_rollout_v1`, `network_er_rollout_v1`, `network_neighbor_list_rollout_v1`, **`resource_cascade_rollout_v1`** — Phase J scaffold).
- Golden scalars live beside the runners (`GOLDEN_METRICS`); CI asserts relaxed numerical agreement.

## Reproduce locally

```powershell
cd fragility-discovery-engine
pip install -e ".[dev]"
python scripts/run_benchmark_suite.py --validate
```

JSON output (no validation):

```powershell
python scripts/run_benchmark_suite.py --json
```

Portable inventory (`benchmark-manifest-v1`):

```powershell
python scripts/run_benchmark_suite.py --manifest-out artifacts/benchmark_manifest.json
```

## Cite a bundle

Use the bundle id, pinned seeds documented in `suite.py` (`_GENOME_SEED`, `_ROLLOUT_SEED`), and record:

- `fragility-engine` git commit SHA,
- Python version,
- `numpy` version.

Example citation fragment:

> Reproduced with `fragility-discovery-engine` bundle `network_er_rollout_v1` at commit `<SHA>` using `python scripts/run_benchmark_suite.py --validate`.

## Ensemble robustness (moonshot)

Topology dispersion for a **fixed** attacker genome:

```powershell
python scripts/fragility_robustness_sweep.py --json --graph-seeds 101,102,103
```

Schema: `fragility-robustness-ensemble-v1` (see `fragility_engine.benchmarks.ensemble`).
