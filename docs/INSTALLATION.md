# Installation and tooling notes

This page **supplements** [`HOW_TO_USE.md`](HOW_TO_USE.md). Use that guide for **Python**, venv, `pip install -e ".[dev]"`, tutorials, and static viewers. Use this page for **Git** and other host-tooling edge cases that are not part of the Python package.

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

## Extra remotes (optional, local only)

Adding another remote (for example to fetch `main` from a second GitHub repository you correlate with this tree) updates **only** your clone’s `.git/config`. Other machines and CI do **not** pick it up until you run the same `git remote add …` there (or restore from a backup of your config). This is normal Git behavior, not something the engine repo needs to track in source control.

---

## Still stuck?

- **Authentication:** sign in once via the credential manager UI when Git prompts during `https://` push or fetch.
- **Python / tests / viewers:** [`HOW_TO_USE.md`](HOW_TO_USE.md) and root [`README.md`](../README.md).
