# coupled_institution (fork scaffold)

Sibling package for **coupled multi-kernel physics** — state exchange inside one `step()`. Not shipped in the main `fragility-engine` charter; see [`docs/FORK_COUPLING_RESEARCH.md`](../../docs/FORK_COUPLING_RESEARCH.md).

## Status

**v0.1** — `CoupledInstitutionWorld` with `step(events, rng)`, fork replay schema `coupled_institution_v1` (`coupled-fork-0.1.0`), rollout + GA demo using main-engine schedule encoding.

**Golden bundle** `coupled_institution_rollout_v1` — pinned schedule in `tests/fixtures/pinned_rollout_schedule.json`, metrics checked by `tests/test_golden_bundle.py`, demo replay at `artifacts/sample_coupled_replay.json` (copied into the main workbench replay viewer on site build).

## Install (editable)

```bash
cd forks/coupled_institution
pip install -e .
pip install -e ../..   # GA demo needs main engine adversary
pytest -q
python scripts/run_coupled_ga_demo.py --export-replay /tmp/coupled_demo.json
python scripts/regenerate_golden.py
python scripts/coupling_strength_sweep.py
python ../../scripts/plot_coupling_sweep.py artifacts/coupling_strength_sweep.json
python scripts/export_coupling_comparison.py
python ../../scripts/export_llm_narration_prompt.py artifacts/sample_coupled_replay.json --prompt-pack coupled_institution_replay_v1
python ../../scripts/export_llm_narration_prompt.py artifacts/coupling_strength_sweep.json --prompt-pack coupled_institution_coupling_sweep_v1
python ../../scripts/export_llm_narration_prompt.py artifacts/sample_coupled_pareto_front.json --prompt-pack coupled_institution_pareto_v1
```

From repo root after regenerate: `python scripts/validate_coupled_fork_bundle.py` (also runs in CI benchmark validate).

**Mutation chain** (attribution viewer): `python scripts/export_coupled_mutation_chain.py` → `artifacts/sample_coupled_mutation_chain.json` (copied to `artifacts/attribution_viewer/` on regenerate).

**Citation certificate:** `python scripts/export_coupled_fork_certificate.py --out /tmp/coupled_cert.json`  
Or embed fork digests in any certificate: `python scripts/export_fragility_certificate.py --out cite.json --research-fork`.

From **repo root** (after `pip install -e ".[dev]"`):

```bash
python scripts/run_coupled_fork_demo.py --regenerate
python scripts/regenerate_coupled_fork_artifacts.py   # also copies into replay_viewer/
python scripts/run_coupled_fork_demo.py --export-replay /tmp/coupled_ga.json
```

## Relationship to main engine

Reuse schedule encoding and search patterns from `fragility-engine`; do not overload `fragility-institutional-composite-v*` JSON as coupled physics.
