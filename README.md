# Railway Authenticated HTTP/HTTPS Proxy

A standalone password-protected **HTTP proxy**. It does not use Tailscale. Railway TCP Proxy provides the public endpoint.

It supports:

- HTTP proxy requests using absolute URLs;
- HTTPS through the `CONNECT` method;
- HTTP Basic proxy authentication;
- Multiple concurrent connections.

## Railway setup

1. Deploy this GitHub repository.
2. In **Variables**, add:

```text
PROXY_USER=<proxy username>
PROXY_PASSWORD=<long random password>
PROXY_PORT=1080
```

3. Deploy and wait for the log:

```text
HTTP proxy listening on 0.0.0.0:1080
```

4. Open **Settings → Networking → TCP Proxy**.
5. Create a TCP Proxy targeting internal port `1080`.
6. Use Railway's generated hostname and external port as an HTTP/HTTPS proxy.

Example with PowerShell:

```powershell
curl.exe -x "http://PROXY_USER:PROXY_PASSWORD@HOST:PORT" https://api.ipify.org
```

Example with environment variables:

```powershell
$env:HTTP_PROXY="http://PROXY_USER:PROXY_PASSWORD@HOST:PORT"
$env:HTTPS_PROXY="http://PROXY_USER:PROXY_PASSWORD@HOST:PORT"
```

No Volume, Tailscale variables, or Tailscale configuration is required. The Railway TCP Proxy is public, so use a long random password and remove the TCP Proxy when it is not needed.

This is an HTTP proxy, not a SOCKS5 proxy. Existing SOCKS5 client settings will not work.