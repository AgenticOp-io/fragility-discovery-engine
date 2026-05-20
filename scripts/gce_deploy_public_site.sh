#!/usr/bin/env bash
# Run on GCE VM: extract public_site tarball into nginx docroot.
set -euo pipefail
SITE_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
ARCHIVE="${1:-${HOME}/fragility-public-site.tar.gz}"

if [[ ! -f "${ARCHIVE}" ]]; then
  echo "error: missing archive ${ARCHIVE}" >&2
  exit 1
fi

bash "${HOME}/gce_install_public_web.sh" 2>/dev/null || bash "$(dirname "$0")/gce_install_public_web.sh"

sudo mkdir -p "${SITE_ROOT}"
sudo rm -rf "${SITE_ROOT:?}"/*
sudo tar -xzf "${ARCHIVE}" -C "${SITE_ROOT}"
sudo chown -R www-data:www-data "${SITE_ROOT}"
sudo systemctl reload nginx
echo "OK: deployed public site to ${SITE_ROOT}"
