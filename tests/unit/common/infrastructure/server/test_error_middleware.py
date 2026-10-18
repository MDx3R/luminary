import json
from typing import Any, cast
from unittest.mock import MagicMock
from uuid import uuid4

from common.application.exceptions import (
    AccessPolicyError,
    DuplicateEntryError,
    NotFoundError,
    OptimisticLockError,
)
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from common.infrastructure.server.fastapi.middleware.error_middleware import (
    ApplicationErrorHandler,
    DomainErrorHandler,
    RepositoryErrorHandler,
    _error_code,
)
from fastapi import status
from fastapi.responses import JSONResponse
from idp.identity.application.exceptions import IdentityNotFoundError


def _body(response: JSONResponse) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(bytes(response.body).decode()))


def test_error_code_not_found() -> None:
    assert _error_code(NotFoundError("x")) == "NOT_FOUND"


def test_error_code_identity_not_found_via_mro() -> None:
    assert _error_code(IdentityNotFoundError("x")) == "NOT_FOUND"


def test_error_code_duplicate() -> None:
    assert _error_code(DuplicateEntryError("username", "bob")) == "DUPLICATE_ENTRY"


def test_application_not_found_status_and_code() -> None:
    request = MagicMock()
    resp = ApplicationErrorHandler().handle(request, NotFoundError("abc"))
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    body = _body(resp)
    assert body["error"] == "NOT_FOUND"
    assert "detail" in body


def test_identity_not_found_status_404() -> None:
    request = MagicMock()
    resp = ApplicationErrorHandler().handle(request, IdentityNotFoundError("abc"))
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert _body(resp)["error"] == "NOT_FOUND"


def test_access_policy() -> None:
    request = MagicMock()
    exc = AccessPolicyError(UserId(uuid4()), "Access denied")
    resp = ApplicationErrorHandler().handle(request, exc)
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert _body(resp)["error"] == "ACCESS_DENIED"


def test_duplicate_entry() -> None:
    request = MagicMock()
    resp = RepositoryErrorHandler().handle(
        request, DuplicateEntryError("username", "bob")
    )
    assert resp.status_code == status.HTTP_409_CONFLICT
    assert _body(resp)["error"] == "DUPLICATE_ENTRY"


def test_optimistic_lock() -> None:
    request = MagicMock()
    resp = RepositoryErrorHandler().handle(request, OptimisticLockError())
    assert resp.status_code == status.HTTP_409_CONFLICT
    body = _body(resp)
    assert body["error"] == "OPTIMISTIC_LOCK"
    assert "Retry later" in body["detail"]


def test_domain_invariant() -> None:
    request = MagicMock()
    resp = DomainErrorHandler().handle(request, InvariantViolationError("bad"))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert _body(resp)["error"] == "INVARIANT_VIOLATION"
