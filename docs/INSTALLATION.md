# Installation notes

This page covers **OS-specific setup**, **Git configuration**, and **repository layout** — edge cases that come up when you are installing for the first time. The main installation steps (Python, venv, `pip install`, running tests) are in [How to Use](/docs/how-to-use.html).

---

## Linux: installing Python and Git

Debian and Ubuntu:

```bash
sudo apt update
sudo apt install -y git python3.12 python3.12-venv
```

If your distribution only ships Python 3.11, replace `3.12` with `3.11` everywhere — both versions are supported. Then follow the venv setup in [How to Use](/docs/how-to-use.html).

**Using WSL (Windows Subsystem for Linux):** clone the repository on the Linux filesystem (for example `~/src/fragility-discovery-engine`) rather than `/mnt/c/...` — file I/O is much faster that way. The same `apt` commands and venv steps apply.

**Fedora / RHEL:** `sudo dnf install -y git python3.12` (or `python3.11`), then the same venv pattern.

**macOS:** install Python 3.11 or newer from [python.org](https://www.python.org/downloads/) or via Homebrew (`brew install python@3.12`), then create a venv with that interpreter.

---

## Git on Windows — fixing a credential warning

### What you might see

After running `git push` or `git fetch`, you get a warning like:

```text
git: 'credential-manager-core' is not a git command. See 'git --help'.
```

The push usually still works, but this warning means Git is looking for a credential helper that does not exist on your system.

### Why it happens

An old setting in your global Git config (`credential.helper=manager-core`) is overriding the working helper that [Git for Windows](https://git-scm.com/download/win) installed. The name `manager-core` comes from old documentation and may not exist on your machine.

### Fix

Remove the override so Git uses its built-in helper:

```powershell
git config --global --unset credential.helper
```

Then run `git fetch` or `git push` once. If Windows prompts you to sign in to GitHub, complete that step — your credentials will be saved for future pushes.

To check what Git is using:

```powershell
git config --show-origin --get-all credential.helper
```

You should see one entry pointing at `manager` from the Git for Windows installation, with no conflicting `manager-core` line.

If you need to set a helper explicitly, use:

```powershell
git config --global credential.helper manager
```

---

## Git over HTTPS on Linux and macOS

Most setups work out of the box using the Git built-in credential helper or the [GitHub CLI](https://cli.github.com/) (`gh auth login`). If `git push` fails:

```bash
# See what credential helper Git is using
git config --show-origin --get-all credential.helper
```

If you get TLS or certificate errors on a minimal server image, install the CA certificates bundle:

```bash
sudo apt install -y ca-certificates   # Debian/Ubuntu
```

---

## Folder layout after cloning

```
fragility-discovery-engine/
  src/fragility_engine/   Library code: simulation worlds, search, explanation
  scripts/                Command-line tools (run from the repo root)
  tests/                  Test suite (400+ tests; run with python -m pytest)
  artifacts/              Bundled demo JSON files and browser-based viewers
  benchmarks/             Benchmark documentation and reference bundles
  docs/                   This documentation set
  pyproject.toml          Package definition and optional extras
```

Install in editable mode from the repo root: `pip install -e ".[dev]"`. The package import name is `fragility_engine`.

---

## Adding a second Git remote (optional)

Adding a remote (`git remote add …`) only changes your local `.git/config`. No other machines or the CI pipeline pick it up unless you run the same command there. This is normal Git behavior.

---

## Running CI checks locally (for contributors)

The automated CI pipeline runs on Ubuntu and Windows against Python 3.11 and 3.12. To run the same checks locally after activating your venv:

| OS | Command |
|----|---------|
| Linux, macOS, WSL | `bash scripts/ci_local.sh` |
| Windows (PowerShell) | `pwsh -File scripts/ci_local.ps1` |

Both scripts run `pip install -e ".[dev]"`, the linter (ruff), pytest, and `python scripts/run_benchmark_suite.py --validate` to confirm the frozen reference results still match. Set `FRAGILITY_CI_LOCAL_BUILD=1` to also build the package wheel (mirrors the CI build job).

---

## Still stuck?

- **Git sign-in on Windows:** let the credential manager UI prompt you on the first `https://` push or fetch, then your credentials will be saved.
- **Git sign-in on Linux/macOS:** use `gh auth login` or your distribution's Git credential documentation.
- **Python, tests, or the browser viewers:** see [How to Use](/docs/how-to-use.html).
