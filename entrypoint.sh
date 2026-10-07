#!/bin/sh
set -eu
: "${PROXY_PORT:=1080}"
: "${PROXY_USER:?Set PROXY_USER}"
: "${PROXY_PASSWORD:?Set PROXY_PASSWORD}"
exec python3 /opt/socks5_server.py --listen 0.0.0.0 --port "$PROXY_PORT" --username "$PROXY_USER" --password "$PROXY_PASSWORD"
