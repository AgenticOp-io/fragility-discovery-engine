# Releasing `fragility-engine`

Version is defined in [`pyproject.toml`](pyproject.toml) as **`[project].version`** (currently **0.6.0**). **`fragility_engine.__version__` must match** before tagging.

## When to tag

- After **`main`** is green (CI: `ruff`, full `pytest`, optional Numba parity).
- Prefer **annotated** tags so `git describe` and provenance fields stay meaningful.

## Steps (maintainer)

```bash
git checkout main
git pull
# confirm pyproject version matches the release you are cutting
grep '^version' pyproject.toml

git tag -a v0.5.0 -m "fragility-engine 0.5.0 — Phase O stretch; see GitHub Releases notes"
git push origin v0.5.0
```

Then on GitHub: **Releases → Draft a new release** → choose the tag → paste a short changelog (link [`docs/WHITEPAPER.md`](docs/WHITEPAPER.md), [`benchmarks/README.md`](benchmarks/README.md), manifest schema **`benchmark-manifest-v2`**).

Attach build artifacts (normal when PyPI is not used):

```bash
python scripts/check_pypi_ready.py --tag v0.5.0
gh release upload v0.5.0 dist/fragility_engine-0.5.0-py3-none-any.whl dist/fragility_engine-0.5.0.tar.gz --clobber
```

Optional **PyPI** (after `PYPI_API_TOKEN` is set): GitHub Actions → **Publish to PyPI** → confirm `publish`. The workflow runs `check_pypi_ready.py` before upload.

## Install a release (no PyPI)

| Method | Command |
|--------|---------|
| **Helper script** (auto: editable if repo matches tag, else Release wheel) | `bash scripts/install_release.sh v0.5.0` or `powershell -NoProfile -File scripts/install_release.ps1 -Tag v0.5.0` |
| **Release wheel** | `pip install https://github.com/AgenticOp-io/fragility-discovery-engine/releases/download/v0.5.0/fragility_engine-0.5.0-py3-none-any.whl` |
| **Git tag** | `pip install "fragility-engine @ git+https://github.com/AgenticOp-io/fragility-discovery-engine.git@v0.5.0"` |
| **Clone + dev** (GCE / contributors) | `pip install -e ".[dev]"` after `git checkout v0.5.0` — see [`scripts/gce_git_deploy.sh`](scripts/gce_git_deploy.sh), [`docs/INSTALLATION.md`](docs/INSTALLATION.md) |

Set `FRAGILITY_INSTALL_MODE=editable|git|wheel` to force a mode. Set `FRAGILITY_REPO` if using a fork mirror.

## Citation hint

Papers and audits should record: **git tag**, **`benchmark_manifest.json`** (from `python scripts/run_benchmark_suite.py --manifest-out …` or CI artifacts), and pinned **replay / Pareto** JSON. See [`docs/PAPER_APPENDIX_WORKFLOW.md`](docs/PAPER_APPENDIX_WORKFLOW.md).
