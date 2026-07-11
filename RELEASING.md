# Releasing `fragility-engine`

Version is defined in [`pyproject.toml`](pyproject.toml) as **`[project].version`** (currently **0.6.0**). **`fragility_engine.__version__` must match** before tagging.

**Version policy:** software tags are `vMAJOR.MINOR.PATCH` (e.g. `v0.6.0`). The FEL / Zenodo archive tag (`fel-v0.1.1`) is a separate scholarly snapshot and may lag the software version.

## When to tag

- After **`main`** is green (CI: `ruff`, full `pytest`, optional Numba parity).
- Prefer **annotated** tags so `git describe` and provenance fields stay meaningful.

## Steps (maintainer)

```bash
git checkout main
git pull
# confirm pyproject version matches the release you are cutting
grep '^version' pyproject.toml

git tag -a v0.6.0 -m "fragility-engine 0.6.0 — BYOW CLI + falsification harness; see GitHub Releases notes"
git push origin v0.6.0
```

Then on GitHub: **Releases → Draft a new release** → choose the tag → paste a short changelog (link [`docs/WHITEPAPER.md`](docs/WHITEPAPER.md), [`AI_READ.md`](AI_READ.md), [`docs/BRING_YOUR_OWN_WORLD.md`](docs/BRING_YOUR_OWN_WORLD.md), [`benchmarks/README.md`](benchmarks/README.md), manifest schema **`benchmark-manifest-v2`**).

Attach build artifacts (normal when PyPI is not used):

```bash
python -m build
python scripts/check_pypi_ready.py --tag v0.6.0
gh release upload v0.6.0 dist/fragility_engine-0.6.0-py3-none-any.whl dist/fragility_engine-0.6.0.tar.gz --clobber
```

Optional **PyPI** (after `PYPI_API_TOKEN` is set): GitHub Actions → **Publish to PyPI** → confirm `publish`. The workflow runs `check_pypi_ready.py` before upload.

## Install a release (no PyPI)

| Method | Command |
|--------|---------|
| **Helper script** (auto: editable if repo matches tag, else Release wheel) | `bash scripts/install_release.sh v0.6.0` or `powershell -NoProfile -File scripts/install_release.ps1 -Tag v0.6.0` |
| **Release wheel** | `pip install https://github.com/AgenticOp-io/fragility-discovery-engine/releases/download/v0.6.0/fragility_engine-0.6.0-py3-none-any.whl` |
| **Git tag** | `pip install "fragility-engine @ git+https://github.com/AgenticOp-io/fragility-discovery-engine.git@v0.6.0"` |
| **Clone + dev** (GCE / contributors) | `pip install -e ".[dev]"` after `git checkout v0.6.0` — see [`scripts/gce_git_deploy.sh`](scripts/gce_git_deploy.sh), [`docs/INSTALLATION.md`](docs/INSTALLATION.md) |

Set `FRAGILITY_INSTALL_MODE=editable|git|wheel` to force a mode. Set `FRAGILITY_REPO` if using a fork mirror.

## Citation hint

Papers and audits should record: **git tag**, **`benchmark_manifest.json`** (from `python scripts/run_benchmark_suite.py --manifest-out …` or CI artifacts), and pinned **replay / Pareto** JSON. See [`docs/PAPER_APPENDIX_WORKFLOW.md`](docs/PAPER_APPENDIX_WORKFLOW.md). Software cite: [`CITATION.cff`](CITATION.cff). Scholarly FEL archive: Zenodo DOI [10.5281/zenodo.20455689](https://doi.org/10.5281/zenodo.20455689) (`fel-v0.1.1`).
