"""Test-only upstream: an auth responder and a backend that echoes identity headers."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/redirect":
            self.send_response(307)
            self.send_header("Location", f"http://{self.headers['Host']}/redirect/")
            self.end_headers()
            return
        if self.path == "/oauth2/auth":
            if self.headers.get("Cookie") != "test_session=valid":
                self.send_response(401)
                self.end_headers()
                return
            self.send_response(202)
            self.send_header("X-Auth-Request-User", "verified-sub")
            self.send_header("X-Auth-Request-Preferred-Username", "verified-name")
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
                    "authorization": self.headers.get("Authorization"),
                }
            ).encode()
        )


if __name__ == "__main__":
    for port in (8000, 4180):
        server = ThreadingHTTPServer(("", port), Handler)
        Thread(target=server.serve_forever, daemon=False).start()
    print("stub ready", flush=True)
