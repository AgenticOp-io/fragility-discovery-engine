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
- [x] **VM hostname context** — `hub.agenticop.io` → `34.61.255.147` is Translation Hub; FDE workbench stays on the IP (`default_server`).
- [x] **Zenodo** — concept [10.5281/zenodo.20455688](https://doi.org/10.5281/zenodo.20455688); v0.6.1 [10.5281/zenodo.21304131](https://doi.org/10.5281/zenodo.21304131) (GitHub→Zenodo sync on release).
- [x] **PyPI** — [`fragility-engine`](https://pypi.org/project/fragility-engine/) (`PYPI_API_TOKEN` secret set).
- [x] **Gravatar / PyPI avatar** — circle-safe `docs/public/assets/logo.png` linked to the PyPI account email.
- [ ] **Optional FDE hostname** — only if you want e.g. `fragility.agenticop.io` (must not steal `hub`).
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
| Zenodo (auto on GitHub Release) | — |
