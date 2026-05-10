#!/usr/bin/env bash
# VM / GCE: pull latest main, editable install, pytest only (no ruff).
# Same deploy-key pattern as gce_pull_and_test.sh — see docs/GCE_DEPLOY_KEY.md.
set -euo pipefail
DEPLOY_DIR="${FRAGILITY_DEPLOY_DIR:-${HOME}/fragility-discovery-engine}"
KEY="${HOME}/.ssh/gce_github_ed25519"
cd "${DEPLOY_DIR}"
if [[ -f "${KEY}" ]]; then
  export GIT_SSH_COMMAND="ssh -i ${KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
fi
git fetch origin main
git checkout main
git pull --ff-only origin main
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -U pip setuptools wheel
pip install -q -e ".[dev]"
python -m pytest -q
echo "OK: pull + pytest"
