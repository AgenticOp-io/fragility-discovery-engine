# Next steps (after clone)

Use this page as a **short checklist** before you change simulation code or open a PR. Deep tutorials stay in [`HOW_TO_USE.md`](HOW_TO_USE.md); normative rules stay in [`BOUNDARIES.md`](../BOUNDARIES.md); direction and backlog tables stay in [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md).

---

## 1. Environment (Linux or Windows)

1. **CPython ≥ 3.11**, `git`, `pip` — see [`HOW_TO_USE.md` §2](HOW_TO_USE.md#2-install-and-verify) and host-specific notes in [`INSTALLATION.md`](INSTALLATION.md).
2. Create and activate a **venv** in the repo root, then `pip install -e ".[dev]"`.

---

## 2. Match CI locally (recommended)

CI runs **Ubuntu + Windows** × Python **3.11 / 3.12** with **ruff**, **pytest**, and `FRAGILITY_PERF_GATE=1` (see `.github/workflows/ci.yml`).

With your venv **activated**:

| Platform | Command |
|----------|---------|
| Linux, macOS, [WSL](https://learn.microsoft.com/windows/wsl/) | `bash scripts/ci_local.sh` |
| Windows PowerShell | `pwsh -File scripts/ci_local.ps1` |

Then optionally:

```bash
python scripts/run_benchmark_suite.py --validate
```

**Google Compute Engine (Linux VM):** after `gcloud auth login`, use [`docs/GCE_DEPLOY_KEY.md`](GCE_DEPLOY_KEY.md) — section **Sync latest `main` on an existing VM** — to `git pull`, `ruff`, and `pytest` with the same perf gate as CI.

---

## 3. Pick work that fits the charter

- **Do not** weaken determinism or world/adversary separation — read [`BOUNDARIES.md`](../BOUNDARIES.md) first.
- **Aspirational ideas** (benchmark metric floors, Phase N fourth domain, narration gaps): see [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) — especially **Near-term backlog** and **Phase N** (draft only until promoted into `BOUNDARIES.md`).
- **Coupled multi-kernel physics:** out of charter here — [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md).

---

## 4. Open a PR

- Prefer **one thin slice** per PR (tests + docs for the behavior you touched).
- Use **[issue templates](https://github.com/theorem6/fragility-discovery-engine/issues/new/choose)** for bugs or reproducibility reports.
