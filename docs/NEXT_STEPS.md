# What's left to do

Everything in the charter (Phases H–N, L, O, P) is shipped on `main` at **v0.5.0**. Only two optional ops items remain open.

## Open items

- [ ] **Custom hostname + HTTPS** — add a DNS A record pointing `fragility.agenticop.io` to `34.61.255.147`, then run `powershell -File scripts/gce_enable_https.ps1`. See `docs/GCE_HTTPS_AND_AUTH.md`.
- [ ] **Deploy keys** — org policy currently blocks them; token sync works fine today. If you want to re-enable: `powershell -File scripts/register_gce_deploy_key.ps1 -GenerateIfMissing`. See `docs/GCE_DEPLOY_KEY.md`.

## Out of scope (by design)

- Hosted SaaS, live market feeds, or regulatory certifications
- LLM-driven policy inside the simulation engine
- A seventh reference domain (open a new charter phase first)

## Maintenance

| Task | Command |
|------|---------|
| Run tests (Windows) | `powershell -File scripts/ci_local.ps1` |
| Run tests (Linux / GCE) | `bash scripts/gce_pull_and_test.sh` |
| Deploy public demo | `powershell -File scripts/gce_deploy_public_site.ps1` |
| Publish GitHub Pages mirror | `powershell -File scripts/deploy_github_pages.ps1` |
| GitHub Actions | Manual only — not triggered on push |
