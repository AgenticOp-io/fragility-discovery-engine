#!/usr/bin/env bash
# Enable HTTPS with Let's Encrypt on the FDE workbench (named host only).
# Does NOT remove the default_server IP vhost (fragility-default-ip).
#
# Prerequisites:
#   1. DNS A record: FRAGILITY_PUBLIC_HOST → this VM's external IP
#   2. Port 443 open (gce_enable_https.ps1 or https-server firewall tag)
#
# Usage:
#   sudo FRAGILITY_PUBLIC_HOST=fragility.agenticop.io bash scripts/gce_install_https.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=gce_nginx_fde.inc.sh
source "${SCRIPT_DIR}/gce_nginx_fde.inc.sh"

HOST="${FRAGILITY_PUBLIC_HOST:-}"
EMAIL="${FRAGILITY_CERTBOT_EMAIL:-admin@agenticop.io}"
SITE_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
NGINX_NAMED="/etc/nginx/sites-available/fragility-public"
CERT_DIR="/etc/letsencrypt/live/${HOST}"

if [[ -z "${HOST}" ]]; then
  echo "Set FRAGILITY_PUBLIC_HOST to an FDE hostname (e.g. fragility.agenticop.io)." >&2
  exit 1
fi
if [[ "${HOST}" == "hub.agenticop.io" || "${HOST}" == "chrysalis.agenticop.io" ]]; then
  echo "error: ${HOST} is reserved for Chrysalis Translation Hub" >&2
  exit 1
fi

if ! command -v certbot >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y certbot
fi

sudo mkdir -p "${SITE_ROOT}/.well-known/acme-challenge"

# ACME on named host only — default-ip vhost untouched.
sudo tee "${NGINX_NAMED}" >/dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${HOST};
    root ${SITE_ROOT};
    location /.well-known/acme-challenge/ { root ${SITE_ROOT}; }
$(_fde_nginx_locations)
}
EOF

sudo ln -sf "${NGINX_NAMED}" /etc/nginx/sites-enabled/fragility-public
sudo nginx -t
sudo systemctl reload nginx

if [[ ! -f "${CERT_DIR}/fullchain.pem" ]]; then
  sudo certbot certonly --webroot -w "${SITE_ROOT}" -d "${HOST}" \
    --non-interactive --agree-tos -m "${EMAIL}" --keep-until-expiring
fi

sudo tee "${NGINX_NAMED}" >/dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${HOST};
    root ${SITE_ROOT};
    location /.well-known/acme-challenge/ { root ${SITE_ROOT}; }
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${HOST};
    ssl_certificate ${CERT_DIR}/fullchain.pem;
    ssl_certificate_key ${CERT_DIR}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
$(_fde_nginx_locations)
}
EOF

sudo nginx -t
sudo systemctl reload nginx
echo "OK: HTTPS enabled for https://${HOST}/"
echo "IP fallback: http://<vm-ip>/ still served by fragility-default-ip"
echo "Renewal: sudo certbot renew"
