#!/bin/bash
# GCE instance startup (runs as root on first boot). Installs tooling + shallow clone + venv + editable install.
# Repo URL is public read-only; for private forks set metadata fragility_repo_url before create (see gce_create_minimal.ps1).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
LOG=/var/log/fragility-bootstrap.log
exec >>"$LOG" 2>&1
echo "=== fragility bootstrap $(date -Is) ==="
sleep 15

apt-get update -qq
apt-get install -y -qq git curl ca-certificates python3.12 python3.12-venv python3-pip build-essential

REPO_URL=$(curl -fsH "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/fragility_repo_url" 2>/dev/null || true)
if [[ -z "${REPO_URL}" ]]; then
  REPO_URL="https://github.com/theorem6/fragility-discovery-engine.git"
fi
REPO_DIR=/home/ubuntu/fragility-discovery-engine

if [[ ! -d "${REPO_DIR}/.git" ]]; then
  rm -rf "${REPO_DIR}"
  sudo -u ubuntu git clone --depth 1 -b main "${REPO_URL}" "${REPO_DIR}"
fi

cd "${REPO_DIR}"
sudo -u ubuntu python3.12 -m venv .venv
sudo -u ubuntu bash -c "cd ${REPO_DIR} && . .venv/bin/activate && pip install -q -U pip setuptools wheel && pip install -q -e '.[dev]'"

echo "=== done $(date -Is) ==="
