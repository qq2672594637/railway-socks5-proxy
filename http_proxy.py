#!/usr/bin/env python3
import argparse
import base64
import hmac
import select
import socket
import socketserver
import threading
from urllib.parse import urlsplit

MAX_HEADER = 64 * 1024


def recv_headers(sock):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("client disconnected")
        data += chunk
        if len(data) > MAX_HEADER:
            raise ValueError("headers too large")
    head, rest = data.split(b"\r\n\r\n", 1)
    lines = head.decode("iso-8859-1").split("\r\n")
    request = lines[0].split(" ", 2)
    if len(request) != 3:
        raise ValueError("bad request line")
    headers = []
    for line in lines[1:]:
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        headers.append((name.strip(), value.lstrip()))
    return request[0].upper(), request[1], request[2], headers, rest


def header_value(headers, name):
    name = name.lower()
    for key, value in headers:
        if key.lower() == name:
            return value
    return None


def auth_ok(headers, expected):
    supplied = header_value(headers, "Proxy-Authorization")
    if not supplied or not supplied.lower().startswith("basic "):
        return False
    try:
        value = base64.b64decode(supplied[6:].strip(), validate=True).decode("utf-8")
    except (ValueError, UnicodeError):
        return False
    return hmac.compare_digest(value, expected)


def target_from(method, target):
    if method == "CONNECT":
        if ":" not in target:
            raise ValueError("CONNECT requires host:port")
        host, port_text = target.rsplit(":", 1)
        return host.strip("[]"), int(port_text), None
    parsed = urlsplit(target)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("HTTP proxy requires an absolute http(s) URL")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    return parsed.hostname, port, path


def relay(client, upstream, initial=b""):
    if initial:
        upstream.sendall(initial)
    sockets = [client, upstream]
    while True:
        ready, _, _ = select.select(sockets, [], [], 300)
        if not ready:
            return
        for source in ready:
            data = source.recv(64 * 1024)
            if not data:
                return
            other = upstream if source is client else client
            other.sendall(data)


class ProxyHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client = self.request
        upstream = None
        try:
            method, target, version, headers, body = recv_headers(client)
            expected = self.server.expected_auth
            if not auth_ok(headers, expected):
                client.sendall(
                    b"HTTP/1.1 407 Proxy Authentication Required\r\n"
                    b"Proxy-Authenticate: Basic realm=proxy\r\n"
                    b"Connection: close\r\nContent-Length: 0\r\n\r\n"
                )
                return
            host, port, path = target_from(method, target)
            upstream = socket.create_connection((host, port), timeout=20)
            upstream.settimeout(None)
            if method == "CONNECT":
                client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                relay(client, upstream, body)
                return

            out = [f"{method} {path} {version}\r\n".encode("iso-8859-1")]
            for name, value in headers:
                if name.lower() in {"proxy-authorization", "proxy-connection", "connection"}:
                    continue
                out.append(f"{name}: {value}\r\n".encode("iso-8859-1"))
            out.append(b"Connection: close\r\n\r\n")
            relay(client, upstream, b"".join(out) + body)
        except (ConnectionError, OSError, ValueError, UnicodeError):
            try:
                client.sendall(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
            except OSError:
                pass
        finally:
            for sock in (client, upstream):
                if sock:
                    try:
                        sock.close()
                    except OSError:
                        pass


class ThreadingProxy(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description="Authenticated HTTP/HTTPS CONNECT proxy")
    parser.add_argument("--listen", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=1080)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    server = ThreadingProxy((args.listen, args.port), ProxyHandler)
    server.expected_auth = f"{args.username}:{args.password}"
    print(f"HTTP proxy listening on {args.listen}:{args.port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()