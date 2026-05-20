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

echo "==> build public site bundle"
python scripts/build_public_site.py

echo "==> server benchmark validate"
python scripts/gce_write_workbench_status.py --out artifacts/public_site/status.json

echo "==> nginx publish"
sudo bash "${SCRIPT_DIR}/gce_install_public_web.sh"
sudo mkdir -p "${PUBLIC_ROOT}"
sudo rm -rf "${PUBLIC_ROOT:?}"/*
sudo cp -a artifacts/public_site/. "${PUBLIC_ROOT}/"
sudo chown -R www-data:www-data "${PUBLIC_ROOT}"
sudo systemctl reload nginx

echo "OK: workbench published to ${PUBLIC_ROOT} (git $(git rev-parse --short HEAD))"
