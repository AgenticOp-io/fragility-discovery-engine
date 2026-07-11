# What's left to do

Charter Phases H–P and **Q–S** are shipped on `main` at **v0.6.0**.

## Shipped in v0.6.0 (Q → S)

| Phase | Deliverable |
|-------|-------------|
| **Q** | Honest README/whitepaper, cite block, version hygiene |
| **R** | `fragility` CLI, `fragility_engine.byow`, `capacity-pool` + `token-bucket` examples |
| **S** | `fragility_engine.falsify`, `fragility falsify search`, `ranked-store` example |

## Distribution / demo

- [x] **GitHub Release v0.6.0** — tag + wheel.
- [x] **Demo guardrails** — anonymous live runs off; API key + rate limit; browse-first copy.
- [ ] **PyPI** — needs repo secret `PYPI_API_TOKEN`, then Actions → Publish to PyPI (or `twine upload`).
- [ ] **Zenodo v0.6.0** — needs `ZENODO_TOKEN`, then `python scripts/publish_zenodo_version.py --tag v0.6.0 --attach-dist --publish`.
- [ ] **Custom hostname + HTTPS** — A record `fragility.agenticop.io` → `34.61.255.147`, then `gce_enable_https.ps1`.
- [ ] **arXiv** — blocked on endorsement.

## Out of scope (by design)

- Hosted SaaS, live market feeds, or regulatory certifications
- LLM-driven policy inside the simulation engine
- A seventh reference domain (open a new charter phase first)
- Coupled mega-institution physics on `main` (fork only)
- Open anonymous compute on the public demo IP

## Maintenance

| Task | Command |
|------|---------|
| Run tests (Windows) | `powershell -File scripts/ci_local.ps1` |
| BYOW smoke | `fragility search --example capacity-pool` |
| Deploy public demo | `powershell -File scripts/gce_deploy_public_site.ps1` |
| Publish GitHub Pages | `powershell -File scripts/deploy_github_pages.ps1` |
| Zenodo version | `python scripts/publish_zenodo_version.py --tag v0.6.0 --attach-dist --publish` |
