#!/usr/bin/env bash
# Idempotent: nginx + /var/www/fragility for public static site.
set -euo pipefail

SITE_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
NGINX_SITE="/etc/nginx/sites-available/fragility-public"

if ! command -v nginx >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
fi

sudo mkdir -p "${SITE_ROOT}"
sudo chown -R "${USER}:${USER}" /var/www/fragility 2>/dev/null || true

sudo tee "${NGINX_SITE}" >/dev/null <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    root ${SITE_ROOT};
    index index.html;
    error_page 404 /404.html;
    location = /404.html { internal; }
    location / {
        try_files \$uri \$uri/ =404;
    }
    # User-generated run artifacts (written by the scenario runner).
    location /runs/ {
        alias ${SITE_ROOT}/runs/;
        autoindex on;
        add_header Cache-Control "no-store" always;
    }
    # Scenario runner backend (loopback only on the VM).
    location /api/ {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 30s;
    }
    add_header X-Fragility-Product "fde-workbench" always;
}
EOF

sudo ln -sf "${NGINX_SITE}" /etc/nginx/sites-enabled/fragility-public
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx
echo "OK: nginx public site root=${SITE_ROOT}"
