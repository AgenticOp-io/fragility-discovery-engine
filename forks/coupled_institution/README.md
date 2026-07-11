# coupled_institution (fork scaffold)

Sibling package for **coupled multi-kernel physics** — state exchange inside one `step()`. Not shipped in the main `fragility-engine` charter; see [`docs/FORK_COUPLING_RESEARCH.md`](../../docs/FORK_COUPLING_RESEARCH.md).

## Status

**v0.4** — four scalars (`P` panic, `O` overload, `L` liquidity, `B` backlog) with `CouplingContract` / `triad_contract()` / `tetra_contract()`, per-step channel metrics, replay schema `coupled-fork-0.4.0`, worth-it bar (two-scalar + triad + tetra), charter in [`CHARTER.md`](CHARTER.md). Extra channels default **off** so golden v1 metrics stay pinned.

## Install (editable)

```bash
cd forks/coupled_institution
pip install -e .
pip install -e ../..   # GA demo needs main engine adversary
pytest -q
python scripts/run_coupled_ga_demo.py --export-replay /tmp/coupled_demo.json
python scripts/run_coupled_ga_demo.py --contract tetra --method ga --generations 2 --population-size 8
python scripts/run_coupled_ga_demo.py --contract tetra --method mc --samples 24
python scripts/regenerate_golden.py
python scripts/coupling_strength_sweep.py
python ../../scripts/plot_coupling_sweep.py artifacts/coupling_strength_sweep.json
python scripts/export_coupling_comparison.py
python ../../scripts/run_coupled_worth_it_bar.py
python ../../scripts/check_coupled_fork_tetra_search.py
python ../../scripts/export_llm_narration_prompt.py artifacts/sample_coupled_replay.json --prompt-pack coupled_institution_replay_v1
python ../../scripts/export_llm_narration_prompt.py artifacts/coupling_strength_sweep.json --prompt-pack coupled_institution_coupling_sweep_v1
python ../../scripts/export_llm_narration_prompt.py artifacts/sample_coupled_pareto_front.json --prompt-pack coupled_institution_pareto_v1
```

From repo root after regenerate: `python scripts/validate_coupled_fork_bundle.py` (also runs in CI benchmark validate).

**Pinned GA Pareto search** — `coupled_institution_pareto_search_v1` (demo budget: seed 61001, 2×10×horizon 10) and **v2** stress tier (seed 61002, 4×16×horizon 12). CI: `python scripts/check_coupled_fork_pareto.py` (both tiers).

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
