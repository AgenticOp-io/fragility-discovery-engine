# Coupled institution research fork — static demo bundle

Frozen JSON from `forks/coupled_institution/artifacts/` for download and citation. Not part of the six-domain charter on `main`.

| File | Role |
|------|------|
| `sample_coupled_replay.json` | Golden coupled rollout (replay viewer) |
| `coupling_strength_sweep.json` | Pinned-schedule sweep over coupling strength |
| `sample_coupling_comparison.json` | Baseline vs variant coupling comparison |
| `sample_coupled_mutation_chain.json` | Mutation-chain path (attribution viewer) |
| `sample_coupled_pareto_front.json` | Small GA Pareto archive (pareto viewer) |
| `coupling_strength_sweep.png` | Static plot of the sweep JSON |

Regenerate: `python scripts/regenerate_coupled_fork_artifacts.py`

LLM prompt bundles (checked in): `artifacts/llm_prompts/coupled_fork_exports/` — regenerate with `python scripts/export_coupled_fork_llm_prompts.py --cite-digest`
