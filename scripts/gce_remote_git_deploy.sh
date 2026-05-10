#!/usr/bin/env bash
# Run ON the GCE VM (after deploy private key is in ~/.ssh/gce_github_ed25519).
# From laptop (repo root), upload BOTH scripts — raw.githubusercontent.com does not work for private repos:
#   gcloud compute scp scripts/gce_git_deploy.sh scripts/gce_remote_git_deploy.sh INSTANCE:/tmp/ --zone=ZONE
#   gcloud compute ssh INSTANCE --zone=ZONE --command='bash /tmp/gce_remote_git_deploy.sh'

set -euo pipefail
chmod 600 "${HOME}/.ssh/gce_github_ed25519"
ssh-keyscan -H github.com >> "${HOME}/.ssh/known_hosts" 2>/dev/null || true
export GIT_SSH_COMMAND="ssh -i ${HOME}/.ssh/gce_github_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
export FRAGILITY_REPO_URL="${FRAGILITY_REPO_URL:-git@github.com:theorem6/fragility-discovery-engine.git}"

sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq curl git python3.11 python3.11-venv

DEPLOY_SCRIPT=/tmp/gce_git_deploy.sh
if [[ ! -f "${DEPLOY_SCRIPT}" ]]; then
  echo "error: missing ${DEPLOY_SCRIPT}. From your laptop run:" >&2
  echo "  gcloud compute scp scripts/gce_git_deploy.sh INSTANCE:${DEPLOY_SCRIPT} --zone=ZONE" >&2
  exit 1
fi
sed -i 's/\r$//' "${DEPLOY_SCRIPT}"
bash "${DEPLOY_SCRIPT}"
