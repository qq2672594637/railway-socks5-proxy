FROM tailscale/tailscale:stable

RUN apk add --no-cache python3

COPY socks5_server.py /opt/socks5_server.py
COPY entrypoint.sh /usr/local/sbin/proxy-entrypoint
RUN chmod 0755 /usr/local/sbin/proxy-entrypoint

ENV TS_USERSPACE=true TS_STATE_DIR=/data/tailscale TS_AUTH_ONCE=true TS_HOSTNAME=railway-socks5-proxy PROXY_PORT=1080

EXPOSE 1080
ENTRYPOINT ["/usr/local/sbin/proxy-entrypoint"]
