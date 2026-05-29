#!/usr/bin/env bash
# Run ON GCE: build public workbench from repo clone, validate benchmarks, publish to nginx.
set -euo pipefail

REPO="${FRAGILITY_DEPLOY_DIR:-${HOME}/fragility-discovery-engine}"
PUBLIC_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -d "${REPO}/.git" ]]; then
  echo "error: missing git clone at ${REPO} — run gce_bootstrap_git.ps1 first" >&2
  exit 1
fi

cd "${REPO}"
if [[ ! -d .venv ]]; then
  PY="$(command -v python3.12 || command -v python3.11 || command -v python3)"
  "${PY}" -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -U pip setuptools wheel
pip install -q -e ".[dev]"
pip install -q -e forks/coupled_institution

echo "==> coupled fork artifacts (replay + attribution samples)"
python scripts/regenerate_coupled_fork_artifacts.py

echo "==> build public site bundle"
python scripts/build_public_site.py

echo "==> server benchmark validate"
python scripts/gce_write_workbench_status.py --out artifacts/public_site/status.json

echo "==> nginx publish"
sudo bash "${SCRIPT_DIR}/gce_install_public_web.sh"
sudo mkdir -p "${PUBLIC_ROOT}/runs"
# Preserve user-generated runs across publishes; replace everything else.
sudo find "${PUBLIC_ROOT}" -mindepth 1 -maxdepth 1 ! -name runs -exec rm -rf {} +
sudo cp -a artifacts/public_site/. "${PUBLIC_ROOT}/"
# Public site directories are read by nginx (www-data); runs/ is written by
# the runner unit (deploy user), so split ownership.
sudo chown -R www-data:www-data "${PUBLIC_ROOT}"
sudo chown -R "${USER}:${USER}" "${PUBLIC_ROOT}/runs"
sudo systemctl reload nginx

echo "==> scenario runner (systemd unit)"
sudo FRAGILITY_DEPLOY_DIR="${REPO}" FRAGILITY_PUBLIC_ROOT="${PUBLIC_ROOT}" SUDO_USER="${USER}" \
  bash "${SCRIPT_DIR}/gce_install_run_server.sh"

echo "OK: workbench published to ${PUBLIC_ROOT} (git $(git rev-parse --short HEAD))"
