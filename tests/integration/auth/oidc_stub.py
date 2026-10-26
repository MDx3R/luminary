"""Isolated test issuer; tests supply signed tokens without a real user account."""

import base64
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs


ISSUER = "http://oidc:8080"
TOKENS: dict[str, str] = {}
ACCESS_TOKENS: dict[str, dict[str, Any]] = {}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/.well-known/openid-configuration":
            self.respond(
                {
                    "issuer": ISSUER,
                    "authorization_endpoint": ISSUER + "/authorize",
                    "token_endpoint": ISSUER + "/token",
                    "introspection_endpoint": ISSUER + "/oauth/v2/introspect",
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
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
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
            claims = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "=="))
            ACCESS_TOKENS[code] = {
                "active": True,
                "sub": claims["sub"],
                "iss": ISSUER,
                "aud": ["project"],
                "exp": int(time.time()) + 3600,
            }
            self.respond(
                {
                    "access_token": code,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "id_token": token,
                }
            )
        elif self.path == "/oauth/v2/introspect":
            expected = "Basic " + base64.b64encode(b"api-client:test-secret").decode()
            if self.headers.get("Authorization") != expected:
                self.send_error(401)
                return
            token = parse_qs(body.decode()).get("token", [""])[0]
            self.respond(ACCESS_TOKENS.get(token, {"active": False}))
        elif self.path == "/test/revoke":
            ACCESS_TOKENS.clear()
            self.respond({})
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
