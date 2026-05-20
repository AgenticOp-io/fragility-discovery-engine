# Next steps (after Phase O + GCE green)

## 1. Release v0.5.0

- [x] GCE validation on `chrysalis-test-vm` ([`GCE_VALIDATION.md`](GCE_VALIDATION.md))
- [x] Tag **v0.5.0** + [GitHub Release](https://github.com/AgenticOp-io/fragility-discovery-engine/releases/tag/v0.5.0) (wheel + sdist)
- [ ] Register GCE deploy key on `AgenticOp-io/fragility-discovery-engine` so `gce_sync_vm.ps1` can `git pull` (see [`archive/GCE_DEPLOY_KEY.md`](archive/GCE_DEPLOY_KEY.md))
- [ ] Optional: run `.github/workflows/pypi.yml` with `PYPI_API_TOKEN` if publishing to PyPI

## 2. External visibility

- [ ] Point **agenticop.io** (or site) at [`WHITEPAPER_INTRODUCTION.md`](WHITEPAPER_INTRODUCTION.md) + flagship demo path
- [ ] Open one GitHub Discussion or issue: “feedback on six-domain benchmark harness”

## 3. Research fork (optional)

- [ ] Flesh out `forks/coupled_institution/` — real `World.step()` coupling + schema bump + golden bundle
- [ ] Or stop at scaffold and cite decoupled **hexa** composite only

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
