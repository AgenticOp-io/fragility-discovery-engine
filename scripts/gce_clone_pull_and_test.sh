#!/usr/bin/env bash
# Run on GCE (e.g. after scp): clone public repo if missing, then full ci_local parity + Phase O smokes.
set -euo pipefail
export GIT_TERMINAL_PROMPT=0
DEPLOY_DIR="${FRAGILITY_DEPLOY_DIR:-${HOME}/fragility-discovery-engine}"
KEY="${HOME}/.ssh/gce_github_ed25519"
MARK="# fragility-discovery-engine: gce-github-deploy"
if [[ -f "${KEY}" ]]; then
  REPO_URL="${FRAGILITY_REPO_URL:-git@github.com:AgenticOp-io/fragility-discovery-engine.git}"
else
  REPO_URL="${FRAGILITY_REPO_URL:-https://github.com/AgenticOp-io/fragility-discovery-engine.git}"
fi
PY="${FRAGILITY_PYTHON:-}"
_self="${BASH_SOURCE[0]:-$0}"
_self_dir="$(cd "$(dirname "${_self}")" && pwd)"

if [[ -f "${HOME}/gce_configure_git_ssh.sh" ]]; then
  # shellcheck source=/dev/null
  source "${HOME}/gce_configure_git_ssh.sh"
  fragility_gce_ensure_github_ssh_config
fi
if [[ -f "${_self_dir}/gce_configure_git_ssh.sh" ]]; then
  # shellcheck source=/dev/null
  source "${_self_dir}/gce_configure_git_ssh.sh"
  fragility_gce_ensure_github_ssh_config
fi

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
  if [[ -f "${KEY}" ]] && ! grep -qF "${MARK}" "${HOME}/.ssh/config" 2>/dev/null; then
    export GIT_SSH_COMMAND="ssh -i ${KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
  fi
  git -c credential.helper= clone --depth 1 -b main "${REPO_URL}" "${DEPLOY_DIR}"
fi
cd "${DEPLOY_DIR}"
for _cfg in "${HOME}/gce_configure_git_ssh.sh" "${DEPLOY_DIR}/scripts/gce_configure_git_ssh.sh"; do
  if [[ -f "${_cfg}" ]]; then
    # shellcheck source=/dev/null
    source "${_cfg}"
    fragility_gce_ensure_github_ssh_config
    break
  fi
done
if [[ -f "${KEY}" ]] && ! grep -qF "${MARK}" "${HOME}/.ssh/config" 2>/dev/null; then
  export GIT_SSH_COMMAND="ssh -i ${KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
fi
git fetch origin main
git checkout main
git pull --ff-only origin main
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
python scripts/run_benchmark_suite.py --validate
python scripts/check_manifest_digest.py
python scripts/check_manifest_inventory.py
python scripts/check_flagship_bundled.py
python scripts/check_manifest_summary.py
python scripts/validate_viewer_presets.py
python scripts/check_bundled_artifacts.py
python scripts/check_bundled_pareto_hypervolume.py
python scripts/fragility_robustness_stretch.py --preset small --dry-run
python scripts/export_static_dashboard.py --out artifacts/dashboard/index.html
python scripts/institutional_composite_demo.py --hexa --horizon 6 | python -c "import json,sys; d=json.load(sys.stdin); assert d['schema']=='fragility-institutional-composite-v5'"
echo "OK: clone/pull + full ci_local parity + Phase O smokes (FRAGILITY_PERF_GATE=${FRAGILITY_PERF_GATE})"
