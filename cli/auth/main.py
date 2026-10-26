"""Infrastructure-only auth_request service; never imported by the Luminary API."""

import math
import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from urllib.parse import quote_plus, urlsplit

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, status


PROFILE_HEADERS = (
    "x-auth-request-user",
    "x-auth-request-name",
    "x-auth-request-email",
)
USERNAME_HEADER = "x-auth-request-preferred-username"
# HTTP header name, not a secret.
TOKEN_HEADER = "x-auth-request-access-token"  # nosec B105


@dataclass(frozen=True)
class Settings:
    issuer: str
    client_id: str
    client_secret: str
    audience: str
    app_origin: str
    session_url: str = "http://oauth2-proxy:4180/oauth2/auth"

    @classmethod
    def from_env(cls) -> "Settings":
        names = (
            "ZITADEL_ISSUER",
            "ZITADEL_API_CLIENT_ID",
            "ZITADEL_API_CLIENT_SECRET",
            "ZITADEL_PROJECT_ID",
            "APP_ORIGIN",
        )
        values = [os.environ[name].strip() for name in names]
        if not all(values):
            raise ValueError("Auth sidecar settings must not be empty")
        return cls(*values)


def session_headers(response: httpx.Response) -> list[tuple[bytes, bytes]]:
    """Keep only unambiguous verified profile fields, preserving UTF-8 bytes."""
    headers = []
    for name in (*PROFILE_HEADERS, USERNAME_HEADER, TOKEN_HEADER):
        value = session_header(response, name)
        if value:
            headers.append((name.encode(), value))
    return headers


def session_header(response: httpx.Response, name: str) -> bytes:
    values = [
        value for key, value in response.headers.raw if key.lower() == name.encode()
    ]
    if len(values) > 1:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    value = values[0] if values else b""
    if any(c in value for c in (b"\r", b"\n", b"\x00")):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if not value.strip() and name != USERNAME_HEADER:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return value if value.strip() else b""


def validate_introspection(payload: object, subject: str, settings: Settings) -> None:
    if not isinstance(payload, dict) or payload.get("active") is not True:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    audience = payload.get("aud")
    audiences = [audience] if isinstance(audience, str) else audience
    if not isinstance(audiences, list) or settings.audience not in audiences:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if payload.get("sub") != subject or payload.get("iss") != settings.issuer:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    validate_expiry(payload.get("exp"))


def validate_expiry(expiry: object) -> None:
    if (
        not isinstance(expiry, (int, float))
        or isinstance(expiry, bool)
        or not math.isfinite(expiry)
        or expiry <= time.time()
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)


async def authorize(
    request: Request, client: httpx.AsyncClient, settings: Settings
) -> Response:
    origin = urlsplit(settings.app_origin)
    # No caller-controlled URLs, identity headers, or bearer credentials are used.
    session = await client.get(
        settings.session_url,
        headers={
            "Cookie": request.headers.get("cookie", ""),
            "Host": origin.netloc,
            "X-Forwarded-Host": origin.netloc,
            "X-Forwarded-Proto": origin.scheme,
        },
    )
    if session.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if session.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE)
    profile = dict(session_headers(session))
    token = profile.pop(TOKEN_HEADER.encode()).decode("utf-8")
    subject = profile[b"x-auth-request-user"].decode("utf-8")
    introspection = await client.post(
        settings.issuer + "/oauth/v2/introspect",
        # OAuth token type hint is a protocol constant, not a secret.
        data={"token": token, "token_type_hint": "access_token"},  # nosec B105
        auth=httpx.BasicAuth(
            quote_plus(settings.client_id), quote_plus(settings.client_secret)
        ),
    )
    if introspection.status_code != status.HTTP_200_OK:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE)
    validate_introspection(introspection.json(), subject, settings)
    response = Response(status_code=status.HTTP_202_ACCEPTED)
    response.raw_headers.extend(profile.items())
    return response


def create_app(
    settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = settings or Settings.from_env()
        async with httpx.AsyncClient(
            timeout=5, follow_redirects=False, trust_env=False, transport=transport
        ) as client:
            app.state.client = client
            yield

    service = FastAPI(
        lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None
    )

    @service.get("/auth")
    async def check(request: Request) -> Response:
        try:
            return await authorize(
                request, request.app.state.client, request.app.state.settings
            )
        except (httpx.HTTPError, ValueError, UnicodeError) as exc:
            # Do not log upstream bodies, cookies, credentials or token values.
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE) from exc

    return service


app = create_app()
