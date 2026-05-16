#!/usr/bin/env bash
# Run on GCE (e.g. after scp): clone public repo if missing, then same as gce_pull_and_test.sh.
set -euo pipefail
export GIT_TERMINAL_PROMPT=0
DEPLOY_DIR="${FRAGILITY_DEPLOY_DIR:-${HOME}/fragility-discovery-engine}"
KEY="${HOME}/.ssh/gce_github_ed25519"
REPO_URL="${FRAGILITY_REPO_URL:-https://github.com/theorem6/fragility-discovery-engine.git}"
PY="${FRAGILITY_PYTHON:-}"
pick_python() {
  if [[ -n "${PY}" ]] && command -v "${PY}" >/dev/null 2>&1; then echo "${PY}"; return 0; fi
  for c in python3.12 python3.11 python3; do
    if command -v "${c}" >/dev/null 2>&1; then
      ver="$("${c}" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
      major="${ver%%.*}"
      minor="${ver#*.}"
      if [[ "${major}" -eq 3 ]] && [[ "${minor}" -ge 11 ]]; then echo "${c}"; return 0; fi
    fi
  done
  echo "error: need Python >= 3.11" >&2
  exit 1
}
if [[ ! -d "${DEPLOY_DIR}/.git" ]]; then
  echo "==> clone ${REPO_URL} -> ${DEPLOY_DIR}"
  mkdir -p "$(dirname "${DEPLOY_DIR}")"
  rm -rf "${DEPLOY_DIR}"
  if [[ -f "${KEY}" ]]; then
    export GIT_SSH_COMMAND="ssh -i ${KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
  fi
  git -c credential.helper= clone --depth 1 -b main "${REPO_URL}" "${DEPLOY_DIR}"
fi
cd "${DEPLOY_DIR}"
if [[ -f "${KEY}" ]]; then
  export GIT_SSH_COMMAND="ssh -i ${KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
fi
git -c credential.helper= fetch origin main
git checkout main
git -c credential.helper= pull --ff-only origin main
PYBIN="$(pick_python)"
if [[ ! -d .venv ]]; then
  "${PYBIN}" -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -U pip setuptools wheel
pip install -q -e ".[dev]"
python -m ruff check .
export FRAGILITY_PERF_GATE="${FRAGILITY_PERF_GATE:-1}"
export FRAGILITY_PERF_GATE_MS="${FRAGILITY_PERF_GATE_MS:-240000}"
python -m pytest -q
echo "OK: clone/pull + ruff + pytest"
