#!/usr/bin/env python3
"""Loopback TCP relay through a reviewed upstream HTTP CONNECT proxy. No request logging."""

import os
import re
import socket
import socketserver
import sys
import threading


def configuration():
    result = {}
    for key in ("UPSTREAM_HOST", "TARGET_HOST"):
        value = os.environ["CHAIN_" + key]
        if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
            raise ValueError("Host must be an IPv4 address or DNS name")
        result[key] = value
    for key in ("UPSTREAM_PORT", "TARGET_PORT", "LISTEN_PORT"):
        value = int(os.environ["CHAIN_" + key])
        if not 1 <= value <= 65535:
            raise ValueError("Port outside valid range")
        result[key] = value
    return result


def tunnel(config):
    upstream = socket.create_connection((config["UPSTREAM_HOST"], config["UPSTREAM_PORT"]), timeout=30)
    try:
        target = f'{config["TARGET_HOST"]}:{config["TARGET_PORT"]}'
        request = f"CONNECT {target} HTTP/1.1\r\nHost: {target}\r\nProxy-Connection: keep-alive\r\n\r\n"
        upstream.sendall(request.encode("ascii"))
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = upstream.recv(4096)
            if not chunk:
                raise ConnectionError("Upstream closed during CONNECT")
            data += chunk
            if len(data) > 65536:
                raise ConnectionError("CONNECT response header too large")
        header, _, remainder = data.partition(b"\r\n\r\n")
        status = header.split(b"\r\n", 1)[0].split()
        if len(status) < 2 or status[0] not in (b"HTTP/1.0", b"HTTP/1.1") or status[1] != b"200":
            raise ConnectionError("Upstream CONNECT rejected")
        upstream.settimeout(None)
        return upstream, remainder
    except Exception:
        upstream.close()
        raise


def pipe(source, destination):
    try:
        while chunk := source.recv(65536):
            destination.sendall(chunk)
    except OSError:
        pass
    finally:
        try:
            destination.shutdown(socket.SHUT_WR)
        except OSError:
            pass


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        upstream = None
        try:
            upstream, remainder = tunnel(self.server.config)
            if remainder:
                self.request.sendall(remainder)
            outgoing = threading.Thread(target=pipe, args=(self.request, upstream), daemon=True)
            outgoing.start()
            pipe(upstream, self.request)
            outgoing.join()
        except (OSError, ValueError):
            print("CONNECT relay failed; inspect upstream connectivity and policy.", file=sys.stderr, flush=True)
        finally:
            if upstream is not None:
                upstream.close()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 128


def main():
    config = configuration()
    with Server(("127.0.0.1", config["LISTEN_PORT"]), Handler) as server:
        server.config = config
        print("Loopback CONNECT relay ready.", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError):
        print("Relay startup failed: check configuration, port ownership and permissions.", file=sys.stderr)
        sys.exit(1)
