# What's left to do

Charter Phases H–P and **Q–S** are shipped on `main` at **v0.6.0**.

## Shipped in v0.6.0 (Q → S)

| Phase | Deliverable |
|-------|-------------|
| **Q** | Honest README/whitepaper, cite block, version hygiene |
| **R** | `fragility` CLI, `fragility_engine.byow`, `capacity-pool` + `token-bucket` examples |
| **S** | `fragility_engine.falsify`, `fragility falsify search`, `ranked-store` example |

## Ops leftovers (optional)

- [ ] **Custom hostname + HTTPS** — `fragility.agenticop.io` → `34.61.255.147`, then `powershell -File scripts/gce_enable_https.ps1`. See `docs/GCE_HTTPS_AND_AUTH.md`.
- [ ] **GitHub Release v0.6.0** — tag + wheel upload per `RELEASING.md`.
- [ ] **Deploy keys** — see `docs/GCE_DEPLOY_KEY.md`.

## Out of scope (by design)

- Hosted SaaS, live market feeds, or regulatory certifications
- LLM-driven policy inside the simulation engine
- A seventh reference domain (open a new charter phase first)
- Coupled mega-institution physics on `main` (fork only)

## Maintenance

| Task | Command |
|------|---------|
| Run tests (Windows) | `powershell -File scripts/ci_local.ps1` |
| Run tests (Linux / GCE) | `bash scripts/gce_pull_and_test.sh` |
| BYOW smoke | `fragility search --example capacity-pool` |
| Falsify smoke | `fragility falsify search --example ranked-store` |
| Deploy public demo | `powershell -File scripts/gce_deploy_public_site.ps1` |
| Publish GitHub Pages mirror | `powershell -File scripts/deploy_github_pages.ps1` |
