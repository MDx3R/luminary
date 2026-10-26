import time

import httpx
import pytest
from cli.auth.main import Settings, authorize, create_app
from fastapi import Request, status
from fastapi.testclient import TestClient


SETTINGS = Settings(
    "http://issuer", "api-client", "test-secret", "project", "http://localhost"
)
PROFILE = {
    "X-Auth-Request-User": "subject",
    "X-Auth-Request-Name": "Jane",
    "X-Auth-Request-Email": "jane@test.io",
    "X-Auth-Request-Access-Token": "session-token",
}


def active_payload() -> dict[str, object]:
    return {
        "active": True,
        "sub": "subject",
        "iss": SETTINGS.issuer,
        "aud": ["project"],
        "exp": int(time.time()) + 60,
    }


def test_sidecar_uses_only_cookie_and_checks_every_request():
    calls = []

    def upstream(request):
        calls.append(request)
        if request.method == "GET":
            assert request.headers["cookie"] == "session=valid"
            assert "authorization" not in request.headers
            assert "x-user-id" not in request.headers
            assert request.headers["host"] == "localhost"
            return httpx.Response(202, headers=PROFILE)
        assert request.url == "http://issuer/oauth/v2/introspect"
        assert request.content == b"token=session-token&token_type_hint=access_token"
        assert request.headers["authorization"].startswith("Basic ")
        return httpx.Response(200, json=active_payload())

    with TestClient(create_app(SETTINGS, httpx.MockTransport(upstream))) as client:
        for _ in range(2):
            response = client.get(
                "/auth",
                headers={
                    "Cookie": "session=valid",
                    "Authorization": "Bearer forged",
                    "X-User-Id": "victim",
                },
            )
            assert response.status_code == status.HTTP_202_ACCEPTED
            assert response.headers["x-auth-request-user"] == "subject"
            assert "x-auth-request-access-token" not in response.headers
    assert [request.method for request in calls] == ["GET", "POST", "GET", "POST"]


@pytest.mark.parametrize(
    "payload",
    [
        {"active": False},
        {"active": "true"},
        {"sub": "another-user"},
        {"aud": ["another-project"]},
        {"iss": "http://attacker"},
        {"exp": 1},
        {"exp": True},
        {"exp": None},
    ],
)
def test_sidecar_rejects_invalid_introspection(payload):
    def upstream(request):
        if request.method == "GET":
            return httpx.Response(202, headers=PROFILE)
        return httpx.Response(200, json=active_payload() | payload)

    with TestClient(create_app(SETTINGS, httpx.MockTransport(upstream))) as client:
        assert client.get("/auth").status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("failure", ["outage", "redirect", "malformed", "wrong-type"])
def test_sidecar_fails_closed_on_upstream_failure(failure):
    def upstream(request):
        if request.method == "GET":
            return httpx.Response(202, headers=PROFILE)
        if failure == "outage":
            raise httpx.ConnectError("unavailable")
        if failure == "redirect":
            return httpx.Response(302, headers={"Location": "http://attacker"})
        if failure == "malformed":
            return httpx.Response(200, text="not-json")
        return httpx.Response(200, json=[])

    with TestClient(create_app(SETTINGS, httpx.MockTransport(upstream))) as client:
        assert client.get("/auth").status_code in (401, 503)


@pytest.mark.parametrize("session_status", [401, 403, 302, 500])
def test_failed_session_never_reaches_introspection(session_status):
    def upstream(request):
        assert request.method == "GET"
        return httpx.Response(session_status)

    with TestClient(create_app(SETTINGS, httpx.MockTransport(upstream))) as client:
        assert client.get("/auth").is_error


@pytest.mark.parametrize("missing", list(PROFILE))
def test_missing_verified_header_is_rejected(missing):
    def upstream(request):
        assert request.method == "GET"
        return httpx.Response(
            202,
            headers={key: value for key, value in PROFILE.items() if key != missing},
        )

    with TestClient(create_app(SETTINGS, httpx.MockTransport(upstream))) as client:
        assert client.get("/auth").status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_profile_utf8_bytes_survive_sidecar():
    headers = [(key.encode(), value.encode()) for key, value in PROFILE.items()]
    headers = [
        (key, "Иван".encode() if key == b"X-Auth-Request-Name" else value)
        for key, value in headers
    ]

    def upstream(request):
        return (
            httpx.Response(202, headers=headers)
            if request.method == "GET"
            else httpx.Response(200, json=active_payload())
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(upstream)) as client:
        response = await authorize(
            Request({"type": "http", "headers": []}), client, SETTINGS
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert dict(response.raw_headers)[b"x-auth-request-name"] == "Иван".encode()
