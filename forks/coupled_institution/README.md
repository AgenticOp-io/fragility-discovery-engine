# coupled_institution (fork scaffold)

Sibling package for **coupled multi-kernel physics** — state exchange inside one `step()`. Not shipped in the main `fragility-engine` charter; see [`docs/FORK_COUPLING_RESEARCH.md`](../../docs/FORK_COUPLING_RESEARCH.md).

## Status

Scaffold only: `CoupledInstitutionWorld` demonstrates a minimal two-scalar coupling (peg panic ↔ cascade overload) with a **schema-bumped** replay mode string `coupled_institution_v0`.

## Install (editable)

```bash
cd forks/coupled_institution
pip install -e .
pytest -q
```

## Relationship to main engine

Reuse schedule encoding and search patterns from `fragility-engine`; do not overload `fragility-institutional-composite-v*` JSON as coupled physics.
