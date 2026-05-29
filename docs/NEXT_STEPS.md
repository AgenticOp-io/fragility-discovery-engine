# Next steps (after Phase O + GCE green)

## 1. Release v0.5.0

- [x] GCE validation on `chrysalis-test-vm` ([`GCE_VALIDATION.md`](GCE_VALIDATION.md))
- [x] Tag **v0.5.0** + [GitHub Release](https://github.com/AgenticOp-io/fragility-discovery-engine/releases/tag/v0.5.0) (wheel + sdist)
- [x] GCE git bootstrap on `chrysalis-test-vm` (`gce_bootstrap_git.ps1`; HTTPS via `gh` token — deploy keys disabled on repo)
- [ ] Re-enable deploy key in GitHub org/repo settings (optional; token sync works today)
- [ ] Optional: run `.github/workflows/pypi.yml` with `PYPI_API_TOKEN` if publishing to PyPI — see [GCE_HTTPS_AND_AUTH.md](GCE_HTTPS_AND_AUTH.md)

## 2. External visibility (Phase P)

- [x] GitHub Pages landing — https://agenticop-io.github.io/fragility-discovery-engine/
- [x] GCE public **product workbench** — `scripts/gce_deploy_public_site.ps1` → http://34.61.255.147/
- [x] Research feedback issue template + pinned feedback issue on GitHub
- [ ] _(Optional, not needed for IP demo)_ Custom hostname + HTTPS — [GCE_HTTPS_AND_AUTH.md](GCE_HTTPS_AND_AUTH.md)

## 3. Research fork

- [x] `forks/coupled_institution/` v0.1 — `step(events)`, replay `coupled_institution_v1`, GA demo ([`phase_p_visibility.md`](phase_p_visibility.md))
- [x] Golden bundle for coupled fork (`coupled_institution_rollout_v1` in `forks/coupled_institution/`)
- [x] CI job `coupled-fork` + root CLIs `run_coupled_fork_demo.py`, `regenerate_coupled_fork_artifacts.py`, `coupling_strength_sweep.py`
- [x] LLM packs (`coupled_institution_replay_v1`, `coupled_institution_coupling_sweep_v1`), narration, `validate_coupled_fork_bundle.py`, manifest `research_fork_bundles`, coupling comparison export
- [x] Public viewers: coupling sweep chart, coupling comparison, mutation chain; `coupled_fork_demo` JSON bundle; workbench `status.json` includes `research_fork_validate`
- [x] Batch LLM exports (`export_coupled_fork_llm_prompts.py`), replay viewer peg+overload series, viewer contract tests
- [x] Coupled fork GA Pareto sample (`export_coupled_fork_pareto.py`), sweep PNG in `coupled_fork_demo`, workbench card + tour step 8

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
