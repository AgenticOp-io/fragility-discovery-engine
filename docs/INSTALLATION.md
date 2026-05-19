# Installation and tooling notes

This page **supplements** [`HOW_TO_USE.md`](HOW_TO_USE.md). Use that guide for **Python**, venv, `pip install -e ".[dev]"`, tutorials, and static viewers. Use this page for **Git**, **OS-specific packages**, and other host-tooling edge cases that are not part of the Python package. **Post-clone checklist** (CI scripts, frozen benchmarks): [`NEXT_STEPS.md`](NEXT_STEPS.md).

## Dual stack (Linux and Windows)

**CI** runs the same checks on **Ubuntu** and **Windows** (Python **3.11** and **3.12**), plus optional **Numba** parity on both (`.github/workflows/ci.yml`). Weekly scheduled regression (`.github/workflows/schedule.yml`) runs the **test** job on **Ubuntu + 3.12** (ruff, pytest with perf gate, explicit **`run_benchmark_suite.py --validate`**, manifest artifact) and a separate **build** job (sdist/wheel + smoke import), mirroring PR CI.

To reproduce the default **test** job locally after activating a venv:

| OS | Command |
|----|---------|
| Linux, macOS, [WSL](https://learn.microsoft.com/windows/wsl/) | `bash scripts/ci_local.sh` |
| Windows (PowerShell) | `pwsh -File scripts/ci_local.ps1` |

Both scripts run `pip install -e ".[dev]"`, **ruff**, **pytest** with `FRAGILITY_PERF_GATE=1`, and **`python scripts/run_benchmark_suite.py --validate`** (frozen golden bundles). Set **`FRAGILITY_CI_LOCAL_BUILD=1`** to also run **`python -m build`** (optional parity with the CI **build** job).

---

## Linux: system Python and venv packages

Debian / Ubuntu examples (adjust version to match **CPython ≥ 3.11**):

```bash
sudo apt update
sudo apt install -y git python3.12 python3.12-venv
```

If your distro ships only **3.11**, use `python3.11` / `python3.11-venv` instead—the engine supports either. Then create the venv as in [`HOW_TO_USE.md`](HOW_TO_USE.md) §2.

**WSL:** clone the repo on the Linux filesystem (for example `~/src/fragility-discovery-engine`) for faster I/O than `/mnt/c/...`; the same `apt` + venv flow applies.

---

## Git credential helper (Windows)

### Symptom

`git push` or `git fetch` prints a warning such as:

```text
git: 'credential-manager-core' is not a git command. See 'git --help'.
```

Pushes may still succeed afterward, but the message means Git is trying to run a **credential helper name that is not on your PATH**.

### Cause

A **global** Git config entry `credential.helper=manager-core` (or similar) can override the **system** helper shipped with [Git for Windows](https://git-scm.com/download/win), which registers the working **Git Credential Manager** as `manager`. The `manager-core` name is easy to copy from older docs and may not resolve as an executable on your install.

### Fix (recommended)

Clear the global override so the system helper is used:

```powershell
git config --global --unset credential.helper
```

Then run `git fetch` or `git push` once; if Windows prompts you to sign in to GitHub, complete that flow so credentials are stored.

To confirm what Git will use:

```powershell
git config --show-origin --get-all credential.helper
```

You should see the **system** entry (Git for Windows install path) pointing at `manager`, and **no** conflicting global `manager-core` line.

### If you must set a helper explicitly

Prefer the value Git for Windows documents for your version, for example:

```powershell
git config --global credential.helper manager
```

Only do this if you understand why the system config is not enough (unusual on a standard Git for Windows setup).

---

## Git over HTTPS (Linux and macOS)

Typical setups use the **Git built-in credential helper** (cache or store) or **[GitHub CLI](https://cli.github.com/)** (`gh auth login`). Distro packages vary; there is no single `manager-core` issue like Git for Windows, but misconfigured `credential.helper` in `~/.gitconfig` can still break pushes.

Useful checks:

```bash
git config --show-origin --get-all credential.helper
```

If `git push` fails with TLS or certificate errors on a minimal server image, install your distro’s **CA certificate** bundle (for example `ca-certificates` on Debian/Ubuntu).

---

## Extra remotes (optional, local only)

Adding another remote (for example to fetch `main` from a second GitHub repository you correlate with this tree) updates **only** your clone’s `.git/config`. Other machines and CI do **not** pick it up until you run the same `git remote add …` there (or restore from a backup of your config). This is normal Git behavior, not something the engine repo needs to track in source control.

---

## Repository layout (after clone)

```
fragility-discovery-engine/
  src/fragility_engine/   # Library: world, adversary, explain, benchmarks, …
  scripts/                # CLI tools (run from repo root)
  tests/                  # Pytest suite (400+ tests; use `python -m pytest`)
  artifacts/              # Checked-in demo JSON + static HTML viewers
  benchmarks/             # Benchmark docs; golden rows in src/…/benchmarks/
  docs/                   # Operator guides — start at docs/README.md
  pyproject.toml          # Package `fragility-engine`, extras: dev, viz, accelerate
```

Install the package in editable mode from the repo root: `pip install -e ".[dev]"`. Import name: `fragility_engine`.

**Tagged release without PyPI:** use [`scripts/install_release.sh`](../scripts/install_release.sh) / [`scripts/install_release.ps1`](../scripts/install_release.ps1) or see [`RELEASING.md`](../RELEASING.md) (GitHub Release wheel, git tag, or editable checkout).

---

## Still stuck?

- **Authentication (Windows):** sign in once via the credential manager UI when Git prompts during `https://` push or fetch.
- **Authentication (Linux/macOS):** use `gh auth login` or your distro’s Git credential documentation.
- **Python / tests / viewers:** [`HOW_TO_USE.md`](HOW_TO_USE.md), [`docs/README.md`](README.md), root [`README.md`](../README.md).
