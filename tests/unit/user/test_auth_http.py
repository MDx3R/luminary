from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from common.application.value_objects.descriptor import IdentityDescriptor
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from luminary.user.application.exceptions import (
    IdentityProviderUnavailableError,
    InvalidIdentityError,
)
from luminary.user.application.interfaces.resolve_user_use_case import (
    IResolveUserUseCase,
)
from luminary.user.presentation.http.fastapi.controllers import user_router


HEADERS = {
    "X-User-Id": "external-subject",
    "X-Username": "jane",
    "Authorization": "Bearer access-token",
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
        "external-subject", "jane", "access-token"
    )


@pytest.mark.parametrize("missing", list(HEADERS))
def test_missing_header_is_unauthorized(client, resolver, missing: str):
    headers = {key: value for key, value in HEADERS.items() if key != missing}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    resolver.execute.assert_not_awaited()


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("Authorization", "Basic abc"),
        ("Authorization", "Bearer"),
        ("Authorization", "Bearer "),
        ("Authorization", "Bearer  access-token"),
        ("Authorization", "Bearer one two"),
        ("Authorization", "Bearer one\ttwo"),
        ("X-User-Id", ""),
        ("X-User-Id", " "),
        ("X-User-Id", " padded "),
        ("X-User-Id", "x" * 256),
        ("X-Username", ""),
        ("X-Username", " "),
    ],
)
def test_invalid_headers_are_unauthorized(client, resolver, name: str, value: str):
    response = client.get("/users/me", headers={**HEADERS, name: value})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    resolver.execute.assert_not_awaited()


@pytest.mark.parametrize("scheme", ["Bearer", "bearer", "BEARER"])
def test_bearer_scheme_is_case_insensitive(client, resolver, scheme: str):
    response = client.get(
        "/users/me", headers={**HEADERS, "Authorization": f"{scheme} access-token"}
    )
    assert response.status_code == status.HTTP_200_OK
    resolver.execute.assert_awaited_once_with(
        "external-subject", "jane", "access-token"
    )


def test_maximum_length_subject_is_accepted(client, resolver):
    subject = "x" * 255
    response = client.get("/users/me", headers={**HEADERS, "X-User-Id": subject})
    assert response.status_code == status.HTTP_200_OK
    resolver.execute.assert_awaited_once_with(subject, "jane", "access-token")


@pytest.mark.parametrize("name", list(HEADERS))
def test_duplicate_identity_headers_are_rejected(client, resolver, name: str):
    response = client.get(
        "/users/me", headers=[*HEADERS.items(), (name, HEADERS[name])]
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    resolver.execute.assert_not_awaited()


@pytest.mark.parametrize(
    ("error", "status_code"),
    [(InvalidIdentityError(), 401), (IdentityProviderUnavailableError(), 503)],
)
def test_identity_errors_are_mapped_without_leaking_tokens(
    client, resolver, error: Exception, status_code: int
):
    resolver.execute.side_effect = error
    response = client.get("/users/me", headers=HEADERS)
    assert response.status_code == status_code
    assert "access-token" not in response.text


@pytest.mark.parametrize(
    "path", ["/users/register", "/auth/login", "/auth/refresh", "/auth/logout"]
)
def test_local_authentication_routes_are_removed(client, path: str):
    assert client.post(path).status_code == status.HTTP_404_NOT_FOUND
