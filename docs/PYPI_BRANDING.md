# PyPI branding (AgenticOps)

Package page metadata ships from `docs/PYPI_README.md` + `[project]` in `pyproject.toml`.
Official mark: **https://agenticop.io/logo.svg** (source: [AgenticOp-io/agenticops-web](https://github.com/AgenticOp-io/agenticops-web)).

## Account avatar (Gravatar)

PyPI user avatars come from [Gravatar](https://gravatar.com), keyed to the email on your PyPI account — PyPI does not host a custom upload for personal accounts.

1. Log in at https://gravatar.com with the **same email** as your PyPI account.
2. Upload `docs/public/assets/logo.png` (or https://agenticop.io/logo.svg exported to PNG).
3. Refresh https://pypi.org/user/&lt;your-username&gt;/ — the AgenticOps mark should appear.

## Organization account (optional)

PyPI [Organization Accounts](https://docs.pypi.org/organization-accounts/) can brand packages under an org name. Community orgs are free (application required); corporate orgs are paid. After approval, transfer `fragility-engine` to the org.

## Re-publish after metadata changes

Bump version → build → `twine upload` (or Actions → Publish to PyPI).
