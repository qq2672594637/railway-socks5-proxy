# Railway Authenticated SOCKS5 Proxy

A password-protected SOCKS5 proxy for Railway. The container also joins Tailscale, but client traffic uses a Railway TCP Proxy.

## Railway

1. Deploy this GitHub repository.
2. Attach a persistent Volume at `/data`.
3. Add Variables:

```text
TS_AUTHKEY=<fresh non-ephemeral Tailscale auth key>
TS_STATE_DIR=/data/tailscale
TS_AUTH_ONCE=true
TS_USERSPACE=true
TS_HOSTNAME=railway-socks5-proxy
PROXY_USER=<proxy username>
PROXY_PASSWORD=<long random password>
PROXY_PORT=1080
```

4. Deploy and confirm logs contain `Authenticated SOCKS5 proxy listening`.
5. Open **Settings -> Networking -> TCP Proxy**, target internal port `1080`.
6. Use the generated public hostname and external port as a SOCKS5 proxy with `PROXY_USER` and `PROXY_PASSWORD`.

Example:

```bash
curl --proxy socks5h://USER:PASSWORD@HOST:PORT https://api.ipify.org
```

Keep the proxy password secret and delete the Railway TCP Proxy when not needed. Do not commit `TS_AUTHKEY` or `PROXY_PASSWORD`.
