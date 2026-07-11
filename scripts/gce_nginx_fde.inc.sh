#!/usr/bin/env bash
# Shared nginx location blocks for the FDE workbench (sourced by gce_install_*.sh).
# Requires: SITE_ROOT

_fde_nginx_locations() {
  cat <<EOF
    root ${SITE_ROOT};
    index index.html;
    error_page 404 /404.html;
    location = /404.html { internal; }
    location / {
        try_files \$uri \$uri/ =404;
    }
    location /runs/ {
        alias ${SITE_ROOT}/runs/;
        autoindex on;
        add_header Cache-Control "no-store" always;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 30s;
    }
    add_header X-Fragility-Product "fde-workbench" always;
EOF
}
