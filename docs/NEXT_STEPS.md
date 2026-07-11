# What's left to do

Charter Phases H–P and **Q–S** are shipped on `main` at **v0.6.5**.

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
- [x] **Zenodo** — concept [10.5281/zenodo.20455688](https://doi.org/10.5281/zenodo.20455688); v0.6.5 *(sync after GitHub Release)*; v0.6.4 [10.5281/zenodo.21312735](https://doi.org/10.5281/zenodo.21312735); v0.6.3 [10.5281/zenodo.21312495](https://doi.org/10.5281/zenodo.21312495).
- [x] **PyPI** — [`fragility-engine`](https://pypi.org/project/fragility-engine/) (`PYPI_API_TOKEN` secret set).
- [x] **Gravatar / PyPI avatar** — circle-safe `docs/public/assets/logo.png` linked to the PyPI account email.
- [x] **Hostname map** — GoDaddy A records + vhosts: [`docs/HOSTNAME_MAP.md`](HOSTNAME_MAP.md); FDE HTTPS live at https://fragility.agenticop.io/; hub directory updated.
- [x] **Operator Intelligence Shorthand** — Chrysalis-inspired tier ladder + CLI (`fragility shorthand`); see [`docs/INTELLIGENCE_SHORTHAND.md`](INTELLIGENCE_SHORTHAND.md).
- [x] **Coupled mega-institution v0.4** — panic/overload/liquidity/backlog tetra, worth-it bar; charter [`forks/coupled_institution/CHARTER.md`](../forks/coupled_institution/CHARTER.md).
- [x] **Tetra under search** — GA/MC demos + `coupled_institution_tetra_rollout_v1` golden + pinned search (`scripts/check_coupled_fork_tetra_search.py`).
- [x] **Paper-appendix tetra digests** — flagship / fork certificates include tetra replay, tetra Pareto, and worth-it bar SHA-256s (`research_fork_validation.tetra_bundle_id`).
- [x] **Workbench tetra + shorthand callouts** — demo table, tour steps, `/docs/intelligence-shorthand.html`.
- [ ] **arXiv** — blocked on endorsement.
- [ ] **Real BYOW adopter** — needs a domain owner with resettable/steppable physics (tutorials alone are not enough).

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
| Zenodo (auto on GitHub Release) | — |
