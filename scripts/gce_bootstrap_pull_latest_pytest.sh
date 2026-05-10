#!/usr/bin/env bash
# One-shot from laptop: scp this to /tmp then ssh bash /tmp/...
# Pulls newest main (needs deploy key on VM), then runs scripts/gce_pull_pytest.sh.
set -euo pipefail
KEY="${HOME}/.ssh/gce_github_ed25519"
if [[ -f "${KEY}" ]]; then
  export GIT_SSH_COMMAND="ssh -i ${KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
fi
cd "${HOME}/fragility-discovery-engine"
git fetch origin main
git checkout main
git pull --ff-only origin main
exec bash scripts/gce_pull_pytest.sh
