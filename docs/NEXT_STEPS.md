# Next steps (after Phase O + GCE green)

## 1. Release v0.5.0

- [x] GCE validation on `chrysalis-test-vm` ([`GCE_VALIDATION.md`](GCE_VALIDATION.md))
- [x] Tag **v0.5.0** + [GitHub Release](https://github.com/AgenticOp-io/fragility-discovery-engine/releases/tag/v0.5.0) (wheel + sdist)
- [x] GCE git bootstrap on `chrysalis-test-vm` (`gce_bootstrap_git.ps1`; HTTPS via `gh` token — deploy keys disabled on repo)
- [ ] Re-enable deploy key in GitHub org/repo settings (optional; token sync works today)
- [ ] Optional: run `.github/workflows/pypi.yml` with `PYPI_API_TOKEN` if publishing to PyPI

## 2. External visibility (Phase P)

- [x] GitHub Pages landing ([`docs/public/index.html`](public/index.html), workflow `pages.yml`) — enable **Settings → Pages → GitHub Actions** once
- [x] Research feedback issue template + pinned feedback issue on GitHub
- [ ] Point **agenticop.io** DNS at Pages URL or repo (operator)

## 3. Research fork

- [x] `forks/coupled_institution/` v0.1 — `step(events)`, replay `coupled_institution_v1`, GA demo ([`phase_p_visibility.md`](phase_p_visibility.md))
- [ ] Golden bundle for coupled fork (fork-only; not `main` charter)

## 4. Not planned on `main`

- Hosted SaaS / live feeds / compliance product
- LLM-driven rollout policy inside physics
- Seventh reference domain without a new charter phase

## 5. Maintenance rhythm

| Cadence | Action |
|---------|--------|
| Each PR | `pwsh -File scripts/ci_local.ps1` locally |
| Before release | `pwsh -File scripts/gce_sync_vm.ps1` |
| Weekly | GitHub **Scheduled regression** workflow (already on `main`) |
