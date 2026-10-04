"""Isolated test issuer; tests supply signed tokens without a real user account."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs


ISSUER = "http://oidc:8080"
TOKENS: dict[str, str] = {}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/.well-known/openid-configuration":
            self.respond(
                {
                    "issuer": ISSUER,
                    "authorization_endpoint": ISSUER + "/authorize",
                    "token_endpoint": ISSUER + "/token",
                    "jwks_uri": ISSUER + "/keys",
                    "response_types_supported": ["code"],
                    "subject_types_supported": ["public"],
                    "id_token_signing_alg_values_supported": ["RS256"],
                    "token_endpoint_auth_methods_supported": ["client_secret_basic"],
                    "code_challenge_methods_supported": ["S256"],
                }
            )
        elif self.path == "/keys":
            self.respond({"keys": [json.loads(os.environ["TEST_JWK"])]})
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"]))
        if self.path == "/test/token":
            payload = json.loads(body)
            TOKENS[payload["code"]] = payload["id_token"]
            self.respond({})
        elif self.path == "/token":
            code = parse_qs(body.decode()).get("code", [""])[0]
            token = TOKENS.pop(code, None)
            if token is None:
                self.send_error(400)
                return
            self.respond(
                {
                    "access_token": "test-access-token",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "id_token": token,
                }
            )
        else:
            self.send_error(404)

    def respond(self, payload: dict[str, Any]) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def log_message(self, format: str, *args) -> None:
        # Do not log authorization codes or token payloads.
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("", 8080), Handler)
    print("issuer ready", flush=True)
    server.serve_forever()
