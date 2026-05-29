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
```

From **repo root** (after `pip install -e ".[dev]"`):

```bash
python scripts/run_coupled_fork_demo.py --regenerate
python scripts/regenerate_coupled_fork_artifacts.py   # also copies into replay_viewer/
python scripts/run_coupled_fork_demo.py --export-replay /tmp/coupled_ga.json
```

## Relationship to main engine

Reuse schedule encoding and search patterns from `fragility-engine`; do not overload `fragility-institutional-composite-v*` JSON as coupled physics.
