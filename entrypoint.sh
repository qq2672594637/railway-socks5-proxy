#!/bin/sh
set -eu
: "${TS_STATE_DIR:=/data/tailscale}"
: "${PROXY_PORT:=1080}"
: "${PROXY_USER:?Set PROXY_USER}"
: "${PROXY_PASSWORD:?Set PROXY_PASSWORD}"
mkdir -p "$TS_STATE_DIR"; chmod 700 "$TS_STATE_DIR"
/usr/local/bin/containerboot &
tailscale_pid=$!
cleanup() { kill "$proxy_pid" "$tailscale_pid" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
python3 /opt/socks5_server.py --listen 0.0.0.0 --port "$PROXY_PORT" --username "$PROXY_USER" --password "$PROXY_PASSWORD" &
proxy_pid=$!
echo "Authenticated SOCKS5 proxy listening on 0.0.0.0:${PROXY_PORT}"
wait "$tailscale_pid"
