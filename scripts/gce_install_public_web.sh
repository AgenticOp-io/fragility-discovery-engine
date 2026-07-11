#!/usr/bin/env bash
# Idempotent: nginx + /var/www/fragility for public static site.
# Creates two vhosts:
#   fragility-default-ip  — default_server :80 (raw IP keeps working)
#   fragility-public      — optional named host on :80 (FRAGILITY_PUBLIC_HOST)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=gce_nginx_fde.inc.sh
source "${SCRIPT_DIR}/gce_nginx_fde.inc.sh"

SITE_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
PUBLIC_HOST="${FRAGILITY_PUBLIC_HOST:-}"
NGINX_DEFAULT="/etc/nginx/sites-available/fragility-default-ip"
NGINX_NAMED="/etc/nginx/sites-available/fragility-public"

if [[ "${PUBLIC_HOST}" == "hub.agenticop.io" || "${PUBLIC_HOST}" == "chrysalis.agenticop.io" ]]; then
  echo "error: ${PUBLIC_HOST} is reserved for Chrysalis Translation Hub" >&2
  exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
fi

sudo mkdir -p "${SITE_ROOT}"
sudo chown -R "${USER}:${USER}" /var/www/fragility 2>/dev/null || true

sudo tee "${NGINX_DEFAULT}" >/dev/null <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
$(_fde_nginx_locations)
}
EOF

if [[ -n "${PUBLIC_HOST}" ]]; then
  sudo tee "${NGINX_NAMED}" >/dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${PUBLIC_HOST};
$(_fde_nginx_locations)
}
EOF
  sudo ln -sf "${NGINX_NAMED}" /etc/nginx/sites-enabled/fragility-public
elif [[ -f "${NGINX_NAMED}" ]] && sudo grep -q "listen 443" "${NGINX_NAMED}" 2>/dev/null; then
  # Keep an existing HTTPS named vhost (installed by gce_install_https.sh).
  echo "OK: preserving existing HTTPS vhost at ${NGINX_NAMED}"
  sudo ln -sf "${NGINX_NAMED}" /etc/nginx/sites-enabled/fragility-public
else
  # No named host requested and no TLS vhost yet — IP-only is fine.
  :
fi

sudo ln -sf "${NGINX_DEFAULT}" /etc/nginx/sites-enabled/fragility-default-ip
sudo rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/fragility-public.bak 2>/dev/null || true
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx
echo "OK: FDE nginx default-ip + root=${SITE_ROOT}"
if [[ -n "${PUBLIC_HOST}" ]]; then
  echo "OK: named host ${PUBLIC_HOST} on :80 (run gce_install_https.sh for TLS)"
fi
