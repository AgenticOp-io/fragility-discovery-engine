# Zenodo archive

Zenodo is linked to GitHub for **AgenticOp-io/fragility-discovery-engine**. Creating a GitHub Release auto-deposits a new version under the concept DOI.

## DOIs

| Kind | DOI | Notes |
|------|-----|-------|
| **Concept** (cite this) | [10.5281/zenodo.20455688](https://doi.org/10.5281/zenodo.20455688) | Always resolves to the latest version |
| Version `v0.6.3` (latest software) | *(pending Zenodo sync after GitHub Release)* | Operator shorthand + coupled tetra |
| Version `v0.6.2` | [10.5281/zenodo.21304265](https://doi.org/10.5281/zenodo.21304265) | Circle-safe AgenticOps mark |
| Version `v0.6.1` | [10.5281/zenodo.21304131](https://doi.org/10.5281/zenodo.21304131) | AgenticOps PyPI branding |
| Version `v0.6.0` | [10.5281/zenodo.21303841](https://doi.org/10.5281/zenodo.21303841) | BYOW CLI + falsification harness |
| Version `fel-v0.1.1` | [10.5281/zenodo.20455689](https://doi.org/10.5281/zenodo.20455689) | FEL preprint snapshot |

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20455688.svg)](https://doi.org/10.5281/zenodo.20455688)
```

## How new versions appear

1. Tag + GitHub Release (e.g. `v0.6.2`) — already how `fel-v0.1.1`, `v0.6.0`, and `v0.6.1` were archived.
2. Zenodo GitHub integration publishes the deposit (usually within minutes).
3. Update [`CITATION.cff`](../CITATION.cff) version DOI list if you want the new version id explicit (concept DOI is enough for most cites).

Optional API path (only if GitHub sync fails): `scripts/publish_zenodo_version.py` with `ZENODO_TOKEN`.

## What gets archived

- GitHub release zip for the tag
- Attached release assets when present

Code is **Apache 2.0**; FEL preprint PDF is **CC BY 4.0**.
