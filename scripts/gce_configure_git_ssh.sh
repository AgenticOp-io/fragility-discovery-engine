#!/usr/bin/env bash
# Idempotent: prepends a Host github.com block so git uses the GCE deploy key without GIT_SSH_COMMAND.
# Run on the VM once (or any time); safe to re-run. See docs/GCE_DEPLOY_KEY.md.
#
# Env:
#   FRAGILITY_GCE_DEPLOY_KEY  Path to private key (default: ~/.ssh/gce_github_ed25519)
#
# When executed: applies config. When sourced: defines fragility_gce_ensure_github_ssh_config only.

fragility_gce_ensure_github_ssh_config() {
  local key="${FRAGILITY_GCE_DEPLOY_KEY:-${HOME}/.ssh/gce_github_ed25519}"
  local mark="# fragility-discovery-engine: gce-github-deploy"
  [[ -f "${key}" ]] || return 0

  mkdir -p "${HOME}/.ssh"
  chmod 700 "${HOME}/.ssh"

  local cfg="${HOME}/.ssh/config"
  if [[ -f "${cfg}" ]] && grep -qF "${mark}" "${cfg}" 2>/dev/null; then
    :
  else
    local key_abs
    key_abs="$(readlink -f "${key}" 2>/dev/null || realpath "${key}" 2>/dev/null || echo "${key}")"
    umask 077
    local tmp
    tmp="$(mktemp)"
    {
      echo "${mark}"
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
}

if [[ -n "${BASH_VERSION:-}" ]] && [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -euo pipefail
  fragility_gce_ensure_github_ssh_config "$@"
fi
