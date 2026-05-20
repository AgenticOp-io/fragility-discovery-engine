#!/usr/bin/env bash
# Shared Git auth for GCE: HTTPS token file (preferred when deploy keys disabled) or SSH deploy key.
# Token file: ~/.config/fragility-engine/github_token (chmod 600), or FRAGILITY_GITHUB_TOKEN.

fragility_gce_github_token() {
  if [[ -n "${FRAGILITY_GITHUB_TOKEN:-}" ]]; then
    printf '%s' "${FRAGILITY_GITHUB_TOKEN}"
    return 0
  fi
  local f="${HOME}/.config/fragility-engine/github_token"
  if [[ -f "${f}" ]]; then
    tr -d '\r\n' <"${f}"
    return 0
  fi
  return 1
}

fragility_gce_git_credential_file() {
  printf '%s' "${HOME}/.config/fragility-engine/git-credentials"
}

fragility_gce_ensure_git_credentials() {
  local token repo cred
  token="$(fragility_gce_github_token)" || return 0
  mkdir -p "${HOME}/.config/fragility-engine"
  chmod 700 "${HOME}/.config/fragility-engine"
  cred="$(fragility_gce_git_credential_file)"
  printf 'https://x-access-token:%s@github.com\n' "${token}" >"${cred}"
  chmod 600 "${cred}"
  repo="${FRAGILITY_REPO_SLUG:-AgenticOp-io/fragility-discovery-engine}"
  export FRAGILITY_GIT_CREDENTIAL_HELPER="store --file=${cred}"
  export FRAGILITY_REPO_URL="https://github.com/${repo}.git"
}

fragility_gce_git_clone_url() {
  local repo="${FRAGILITY_REPO_SLUG:-AgenticOp-io/fragility-discovery-engine}"
  if fragility_gce_github_token >/dev/null; then
    printf 'https://github.com/%s.git\n' "${repo}"
    return 0
  fi
  if [[ -f "${HOME}/.ssh/gce_github_ed25519" ]]; then
    printf 'git@github.com:%s.git\n' "${repo}"
    return 0
  fi
  printf 'https://github.com/%s.git\n' "${repo}"
}

fragility_gce_git_env() {
  fragility_gce_ensure_git_credentials
  if [[ -n "${FRAGILITY_GIT_CREDENTIAL_HELPER:-}" ]]; then
    export GIT_TERMINAL_PROMPT=0
  fi
}

fragility_gce_git() {
  fragility_gce_git_env
  if [[ -n "${FRAGILITY_GIT_CREDENTIAL_HELPER:-}" ]]; then
    git -c "credential.helper=${FRAGILITY_GIT_CREDENTIAL_HELPER}" "$@"
  else
    git "$@"
  fi
}
