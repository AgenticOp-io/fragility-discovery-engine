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
  REPO_URL="https://github.com/AgenticOp-io/fragility-discovery-engine.git"
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
    sudo -u ubuntu bash <<'UBOOTSTRAP'
set -euo pipefail
export HOME=/home/ubuntu
KEY="${HOME}/.ssh/gce_github_ed25519"
MARK="# fragility-discovery-engine: gce-github-deploy"
mkdir -p "${HOME}/.ssh"
chmod 700 "${HOME}/.ssh"
cfg="${HOME}/.ssh/config"
if [[ -f "${cfg}" ]] && grep -qF "${MARK}" "${cfg}" 2>/dev/null; then
  :
else
  key_abs="$(readlink -f "${KEY}" 2>/dev/null || realpath "${KEY}" 2>/dev/null || echo "${KEY}")"
  umask 077
  tmp="$(mktemp)"
  {
    echo "${MARK}"
    echo "Host github.com"
    echo "  HostName github.com"
    echo "  User git"
    echo "  IdentityFile ${key_abs}"
    echo "  IdentitiesOnly yes"
    echo "  StrictHostKeyChecking accept-new"
    echo ""
  } >"${tmp}"
  if [[ -f "${cfg}" ]]; then
    cat "${cfg}" >>"${tmp}"
  fi
  mv "${tmp}" "${cfg}"
  chmod 600 "${cfg}"
fi
touch "${HOME}/.ssh/known_hosts"
chmod 600 "${HOME}/.ssh/known_hosts"
if ! ssh-keygen -F github.com -f "${HOME}/.ssh/known_hosts" >/dev/null 2>&1; then
  ssh-keyscan -H github.com >>"${HOME}/.ssh/known_hosts" 2>/dev/null || true
fi
UBOOTSTRAP
    sudo -u ubuntu -H git clone --depth 1 -b main "${REPO_URL}" "${REPO_DIR}"
  else
    sudo -u ubuntu git -c credential.helper= clone --depth 1 -b main "${REPO_URL}" "${REPO_DIR}"
  fi
fi

cd "${REPO_DIR}"
PYBIN="$(command -v python3)"
sudo -u ubuntu "${PYBIN}" -m venv .venv
sudo -u ubuntu bash -c "cd ${REPO_DIR} && . .venv/bin/activate && pip install -q -U pip setuptools wheel && pip install -q -e '.[dev]'"

echo "=== done $(date -Is) ==="
