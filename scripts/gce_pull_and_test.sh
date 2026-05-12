#!/usr/bin/env bash
# Run on GCE after scp: bash ~/gce_pull_and_test.sh
# Uses deploy key if present (private repo); otherwise plain git pull.
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
python -m ruff check .
# Match .github/workflows/ci.yml test job (perf gate on benchmark suite)
export FRAGILITY_PERF_GATE="${FRAGILITY_PERF_GATE:-1}"
export FRAGILITY_PERF_GATE_MS="${FRAGILITY_PERF_GATE_MS:-240000}"
python -m pytest -q
echo "OK: pull + ruff + pytest (FRAGILITY_PERF_GATE=${FRAGILITY_PERF_GATE})"
