#!/bin/bash
# GCE instance startup (runs as root on first boot). Installs tooling + shallow clone + venv + editable install.
# Works on Ubuntu 24.04+ and Debian 12+ (default ``python3`` + ``python3-venv``, not hard-coded 3.12).
# Private repo: set metadata ``fragility_repo_url`` to ``git@github.com:…`` and install deploy key for ``ubuntu`` (see docs/GCE_DEPLOY_KEY.md).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
export GIT_TERMINAL_PROMPT=0
LOG=/var/log/fragility-bootstrap.log
exec >>"$LOG" 2>&1
echo "=== fragility bootstrap $(date -Is) ==="
sleep 15

apt-get update -qq
apt-get install -y -qq git curl ca-certificates build-essential python3-pip python3-venv

REPO_URL=$(curl -fsH "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/fragility_repo_url" 2>/dev/null || true)
if [[ -z "${REPO_URL}" ]]; then
  REPO_URL="https://github.com/theorem6/fragility-discovery-engine.git"
fi
REPO_DIR=/home/ubuntu/fragility-discovery-engine
UBUNTU_KEY=/home/ubuntu/.ssh/gce_github_ed25519

if [[ ! -d "${REPO_DIR}/.git" ]]; then
  rm -rf "${REPO_DIR}"
  if [[ "${REPO_URL}" == git@* ]]; then
    if [[ ! -f "${UBUNTU_KEY}" ]]; then
      echo "error: SSH repo URL but missing ${UBUNTU_KEY}" >&2
      exit 1
    fi
    chown ubuntu:ubuntu "${UBUNTU_KEY}"
    chmod 600 "${UBUNTU_KEY}"
    sudo -u ubuntu mkdir -p /home/ubuntu/.ssh
    sudo -u ubuntu bash -c "ssh-keyscan -H github.com >> /home/ubuntu/.ssh/known_hosts 2>/dev/null || true"
    sudo -u ubuntu bash -c "export GIT_SSH_COMMAND=\"ssh -i ${UBUNTU_KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new\"; git clone --depth 1 -b main \"${REPO_URL}\" \"${REPO_DIR}\""
  else
    sudo -u ubuntu git -c credential.helper= clone --depth 1 -b main "${REPO_URL}" "${REPO_DIR}"
  fi
fi

cd "${REPO_DIR}"
PYBIN="$(command -v python3)"
sudo -u ubuntu "${PYBIN}" -m venv .venv
sudo -u ubuntu bash -c "cd ${REPO_DIR} && . .venv/bin/activate && pip install -q -U pip setuptools wheel && pip install -q -e '.[dev]'"

echo "=== done $(date -Is) ==="
