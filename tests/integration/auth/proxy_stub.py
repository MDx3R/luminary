"""Test-only upstream: an auth responder and a backend that echoes identity headers."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from socketserver import ThreadingUnixStreamServer
from threading import Thread


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/redirect":
            self.send_response(307)
            self.send_header("Location", f"http://{self.headers['Host']}/redirect/")
            self.end_headers()
            return
        if self.path in ("/oauth2/auth", "/auth"):
            if self.headers.get("Cookie") != "test_session=valid":
                self.send_response(401)
                self.end_headers()
                return
            self.send_response(202)
            self.send_header("X-Auth-Request-User", "verified-sub")
            self.send_header("X-Auth-Request-Preferred-Username", "verified-name")
            self.send_header("X-Auth-Request-Name", "Verified Name")
            self.send_header("X-Auth-Request-Email", "verified@example.com")
            self.send_header("X-Auth-Request-Access-Token", "verified-token")
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "subject": self.headers.get("X-User-Id"),
                    "username": self.headers.get("X-Username"),
                    "name": self.headers.get("X-User-Name"),
                    "email": self.headers.get("X-Email"),
                    "authorization": self.headers.get("Authorization"),
                    "cookie": self.headers.get("Cookie"),
                    "proxy_authorization": self.headers.get("Proxy-Authorization"),
                    "forwarded_token": self.headers.get("X-Forwarded-Access-Token"),
                    "auth_request_token": self.headers.get(
                        "X-Auth-Request-Access-Token"
                    ),
                }
            ).encode()
        )

    def log_message(self, format: str, *args) -> None:
        pass


if __name__ == "__main__":
    socket_path = "/run/luminary/app.sock"
    socket_server = ThreadingUnixStreamServer(socket_path, Handler)
    os.chmod(socket_path, 0o666)
    Thread(target=socket_server.serve_forever, daemon=False).start()
    for port in (4180, 4181):
        server = ThreadingHTTPServer(("", port), Handler)
        Thread(target=server.serve_forever, daemon=False).start()
    print("stub ready", flush=True)
