# Railway Authenticated SOCKS5 Proxy

A standalone password-protected SOCKS5 proxy. It does **not** use Tailscale; Railway TCP Proxy provides the public endpoint.

## Railway setup

1. Deploy this GitHub repository.
2. In **Variables**, add:

```text
PROXY_USER=<proxy username>
PROXY_PASSWORD=<long random password>
PROXY_PORT=1080
```

3. Deploy and wait for the service to start.
4. Open **Settings → Networking → TCP Proxy**.
5. Create a TCP Proxy targeting internal port `1080`.
6. Use Railway's generated hostname and external port as a SOCKS5 proxy with the configured username and password.

Example:

```bash
curl --proxy socks5h://USER:PASSWORD@HOST:PORT https://api.ipify.org
```

No Volume, Tailscale variables, public domain, or Tailscale configuration is required. The Railway TCP Proxy is public, so use a long random password and delete the TCP Proxy when it is not needed.
