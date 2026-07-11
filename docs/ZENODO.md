# Zenodo archive

Zenodo gives a **citable DOI** for this project. Prefer the **concept DOI** so citations resolve to the latest version.

## DOIs

| Kind | DOI | Notes |
|------|-----|-------|
| **Concept** (cite this) | [10.5281/zenodo.20455688](https://doi.org/10.5281/zenodo.20455688) | Always points at latest published version |
| Version `fel-v0.1.1` | [10.5281/zenodo.20455689](https://doi.org/10.5281/zenodo.20455689) | FEL preprint + citation snapshot |
| Version `0.6.0` | minted when published via `scripts/publish_zenodo_version.py` | Software release (BYOW CLI + falsify) |

Badge (concept DOI preferred going forward):

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20455688.svg)](https://doi.org/10.5281/zenodo.20455688)
```

The older badge `10.5281/zenodo.20455689` still resolves to the FEL snapshot version.

## Enable (once — done)

1. Sign in at [zenodo.org](https://zenodo.org) (GitHub OAuth).
2. **Account → GitHub** → enable **AgenticOp-io/fragility-discovery-engine**.
3. GitHub releases may create **draft** deposits; publish them, or use the script below.

## Publish a software version (recommended)

```powershell
$env:ZENODO_TOKEN = "<token with deposit:write + deposit:actions>"
python -m build
python scripts/publish_zenodo_version.py --tag v0.6.0 --attach-dist --publish
```

Omit `--publish` to leave a draft for manual review at zenodo.org.

After publish, update [`CITATION.cff`](../CITATION.cff) `identifiers` / notes if you want the version DOI listed explicitly (concept DOI is enough for most cites).

## What gets archived

- Release tarball / uploaded wheel + sdist
- Metadata: version, Apache 2.0, link to GitHub tag

Code is **Apache 2.0**; FEL preprint PDF is **CC BY 4.0**.
