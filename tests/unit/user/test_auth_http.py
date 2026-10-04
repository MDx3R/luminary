from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from common.application.value_objects.descriptor import IdentityDescriptor
from common.presentation.http.fastapi.auth import get_proxy_identity
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.testclient import TestClient

from luminary.user.application.dtos.profile import ExternalProfile
from luminary.user.application.interfaces.resolve_user_use_case import (
    IResolveUserUseCase,
)
from luminary.user.presentation.http.fastapi.controllers import user_router


HEADERS = {
    "X-User-Id": "external-subject",
    "X-Username": "jane",
    "X-User-Name": "Jane Doe",
    "X-Email": "jane@example.com",
}


@pytest.fixture
def resolver():
    resolver = AsyncMock(spec=IResolveUserUseCase)
    resolver.execute.return_value = IdentityDescriptor(
        uuid4(), "jane", "Jane Doe", "jane@example.com"
    )
    return resolver


@pytest.fixture
def client(resolver):
    app = FastAPI()
    app.include_router(user_router, prefix="/users")
    app.dependency_overrides[IResolveUserUseCase] = lambda: resolver
    with TestClient(app) as client:
        yield client


def test_me_returns_product_profile(client, resolver):
    response = client.get("/users/me", headers=HEADERS)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(resolver.execute.return_value.identity_id),
        "name": "Jane Doe",
        "email": "jane@example.com",
    }
    resolver.execute.assert_awaited_once_with(
        ExternalProfile("external-subject", "Jane Doe", "jane@example.com"), "jane"
    )


@pytest.mark.parametrize("missing", list(HEADERS))
def test_missing_header_is_unauthorized(client, resolver, missing: str):
    headers = {key: value for key, value in HEADERS.items() if key != missing}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "WWW-Authenticate" not in response.headers
    resolver.execute.assert_not_awaited()


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("X-User-Id", ""),
        ("X-User-Id", " "),
        ("X-User-Id", " padded "),
        ("X-User-Id", "x" * 256),
        ("X-Username", ""),
        ("X-Username", " "),
        ("X-User-Name", ""),
        ("X-User-Name", " "),
        ("X-Email", ""),
        ("X-Email", " "),
    ],
)
def test_invalid_headers_are_unauthorized(client, resolver, name: str, value: str):
    response = client.get("/users/me", headers={**HEADERS, name: value})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    resolver.execute.assert_not_awaited()


def test_tokens_or_cookies_alone_cannot_resolve_a_user(client, resolver):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer token", "Cookie": "session=opaque"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    resolver.execute.assert_not_awaited()


def test_maximum_length_subject_is_accepted(client, resolver):
    subject = "x" * 255
    response = client.get("/users/me", headers={**HEADERS, "X-User-Id": subject})
    assert response.status_code == status.HTTP_200_OK
    resolver.execute.assert_awaited_once_with(
        ExternalProfile(subject, "Jane Doe", "jane@example.com"), "jane"
    )


@pytest.mark.parametrize("name", list(HEADERS))
def test_duplicate_identity_headers_are_rejected(client, resolver, name: str):
    response = client.get(
        "/users/me", headers=[*HEADERS.items(), (name, HEADERS[name])]
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    resolver.execute.assert_not_awaited()


def test_utf8_profile_headers_are_decoded(client, resolver):
    name = "Анна Иванова"
    headers = {**HEADERS, "X-User-Name": name}
    response = client.get(
        "/users/me", headers=[(k.encode(), v.encode()) for k, v in headers.items()]
    )
    assert response.status_code == status.HTTP_200_OK
    resolver.execute.assert_awaited_once_with(
        ExternalProfile("external-subject", name, "jane@example.com"), "jane"
    )


def test_invalid_utf8_profile_header_is_rejected():
    headers = [
        (k.lower().encode(), v.encode())
        for k, v in HEADERS.items()
        if k != "X-User-Name"
    ]
    request = Request(
        {"type": "http", "headers": [*headers, (b"x-user-name", b"\xff")]}
    )
    with pytest.raises(HTTPException) as error:
        get_proxy_identity(request)
    assert error.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "path", ["/users/register", "/auth/login", "/auth/refresh", "/auth/logout"]
)
def test_local_authentication_routes_are_removed(client, path: str):
    assert client.post(path).status_code == status.HTTP_404_NOT_FOUND
