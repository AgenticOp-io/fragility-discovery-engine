#!/usr/bin/env bash
# Clone or pull fragility-discovery-engine on a Linux VM (e.g. GCE) — faster than tarball/scp.
#
# Public repo (default):
#   sudo apt-get update && sudo apt-get install -y git python3.11 python3.11-venv
#   curl -fsSL https://raw.githubusercontent.com/AgenticOp-io/fragility-discovery-engine/main/scripts/gce_git_deploy.sh | bash
#
# Private repo: set FRAGILITY_REPO_URL to an SSH remote or HTTPS with a token (do not commit secrets):
#   export FRAGILITY_REPO_URL='git@github.com:AgenticOp-io/fragility-discovery-engine.git'
#   bash scripts/gce_git_deploy.sh
#
# Env:
#   FRAGILITY_REPO_URL   — git remote (default: https://github.com/AgenticOp-io/fragility-discovery-engine.git)
#   FRAGILITY_DEPLOY_DIR — target directory (default: $HOME/fragility-discovery-engine)
#   FRAGILITY_BRANCH     — branch (default: main)
#   FRAGILITY_PYTHON     — python executable (default: first of python3.12, python3.11, python3 with version >= 3.11)
#   FRAGILITY_RUN_TESTS  — set to 1 to run ``python -m pytest`` after install (default: 0)
#   FRAGILITY_SHALLOW    — set to 0 for full clone history (default: 1)

set -euo pipefail

FRAGILITY_REPO_URL="${FRAGILITY_REPO_URL:-https://github.com/AgenticOp-io/fragility-discovery-engine.git}"
FRAGILITY_DEPLOY_DIR="${FRAGILITY_DEPLOY_DIR:-${HOME}/fragility-discovery-engine}"
FRAGILITY_BRANCH="${FRAGILITY_BRANCH:-main}"
FRAGILITY_PYTHON="${FRAGILITY_PYTHON:-}"
FRAGILITY_RUN_TESTS="${FRAGILITY_RUN_TESTS:-0}"
FRAGILITY_SHALLOW="${FRAGILITY_SHALLOW:-1}"

pick_python() {
  if [[ -n "${FRAGILITY_PYTHON}" ]] && command -v "${FRAGILITY_PYTHON}" >/dev/null 2>&1; then
    echo "${FRAGILITY_PYTHON}"
    return 0
  fi
  local c ver major minor
  for c in python3.12 python3.11 python3; do
    if command -v "${c}" >/dev/null 2>&1; then
      ver="$("${c}" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
      major="${ver%%.*}"
      minor="${ver#*.}"
      if [[ "${major}" -eq 3 ]] && [[ "${minor}" -ge 11 ]]; then
        echo "${c}"
        return 0
      fi
    fi
  done
  echo "error: need Python >= 3.11 (e.g. sudo apt-get install -y python3.11 python3.11-venv)" >&2
  exit 1
}

sync_repo() {
  if [[ -d "${FRAGILITY_DEPLOY_DIR}" ]] && [[ ! -d "${FRAGILITY_DEPLOY_DIR}/.git" ]]; then
    echo "==> removing non-git directory: ${FRAGILITY_DEPLOY_DIR}"
    rm -rf "${FRAGILITY_DEPLOY_DIR}"
  fi
  if [[ -d "${FRAGILITY_DEPLOY_DIR}/.git" ]]; then
    echo "==> git pull ${FRAGILITY_BRANCH} in ${FRAGILITY_DEPLOY_DIR}"
    git -C "${FRAGILITY_DEPLOY_DIR}" fetch origin "${FRAGILITY_BRANCH}"
    git -C "${FRAGILITY_DEPLOY_DIR}" checkout "${FRAGILITY_BRANCH}"
    git -C "${FRAGILITY_DEPLOY_DIR}" pull --ff-only origin "${FRAGILITY_BRANCH}"
  else
    echo "==> git clone -> ${FRAGILITY_DEPLOY_DIR}"
    mkdir -p "$(dirname "${FRAGILITY_DEPLOY_DIR}")"
    local depth_args=()
    if [[ "${FRAGILITY_SHALLOW}" == "1" ]]; then
      depth_args=(--depth 1)
    fi
    git clone "${depth_args[@]}" -b "${FRAGILITY_BRANCH}" "${FRAGILITY_REPO_URL}" "${FRAGILITY_DEPLOY_DIR}"
  fi
}

PYBIN="$(pick_python)"
echo "==> using ${PYBIN} ($("${PYBIN}" -V))"

sync_repo

cd "${FRAGILITY_DEPLOY_DIR}"
echo "==> venv + pip install -e '.[dev]'"
"${PYBIN}" -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -e ".[dev]"

if [[ "${FRAGILITY_RUN_TESTS}" == "1" ]]; then
  echo "==> ruff + pytest (CI-like perf gate)"
  python -m ruff check .
  export FRAGILITY_PERF_GATE="${FRAGILITY_PERF_GATE:-1}"
  export FRAGILITY_PERF_GATE_MS="${FRAGILITY_PERF_GATE_MS:-240000}"
  python -m pytest -q
fi

echo "==> done. Activate: source ${FRAGILITY_DEPLOY_DIR}/.venv/bin/activate"
