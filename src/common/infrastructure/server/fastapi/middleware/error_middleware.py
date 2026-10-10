from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import ClassVar

from common.application.exceptions import (
    AccessPolicyError,
    ApplicationError,
    DuplicateEntryError,
    NotFoundError,
    OptimisticLockError,
    RepositoryError,
)
from common.domain.exceptions import DomainError
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


def _error_code(exc: BaseException) -> str:
    """Код из ClassVar `code` по MRO, иначе INTERNAL_ERROR."""
    for cls in type(exc).__mro__:
        code = cls.__dict__.get("code")
        if isinstance(code, str):
            return code
    return "INTERNAL_ERROR"


def _status_for(
    exc: Exception, status_map: dict[type[Exception], int], default: int
) -> int:
    for cls in type(exc).__mro__:
        if cls in status_map:
            return status_map[cls]
    return default


def _json_error(
    status_code: int, exc: Exception, *, safe_detail: bool = False
) -> JSONResponse:
    detail = "Internal server error" if safe_detail else str(exc)
    return JSONResponse(
        status_code=status_code,
        content={"error": _error_code(exc), "detail": detail},
    )


class IHTTPErrorHandler(ABC):
    @abstractmethod
    def can_handle(self, exc: Exception) -> bool: ...

    @abstractmethod
    def handle(self, request: Request, exc: Exception) -> JSONResponse: ...


class DomainErrorHandler(IHTTPErrorHandler):
    def can_handle(self, exc: Exception) -> bool:
        return isinstance(exc, DomainError)

    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        return _json_error(status.HTTP_400_BAD_REQUEST, exc)


class ApplicationErrorHandler(IHTTPErrorHandler):
    ERROR_STATUS_MAP: ClassVar[dict[type[Exception], int]] = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        AccessPolicyError: status.HTTP_403_FORBIDDEN,
    }

    def can_handle(self, exc: Exception) -> bool:
        return isinstance(exc, ApplicationError)

    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        status_code = _status_for(
            exc, self.ERROR_STATUS_MAP, status.HTTP_400_BAD_REQUEST
        )
        return _json_error(status_code, exc)


class RepositoryErrorHandler(IHTTPErrorHandler):
    ERROR_STATUS_MAP: ClassVar[dict[type[Exception], int]] = {
        DuplicateEntryError: status.HTTP_409_CONFLICT,
        OptimisticLockError: status.HTTP_409_CONFLICT,
    }

    def can_handle(self, exc: Exception) -> bool:
        return isinstance(exc, RepositoryError)

    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        status_code = _status_for(
            exc, self.ERROR_STATUS_MAP, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        if isinstance(exc, OptimisticLockError):
            return JSONResponse(
                status_code=status_code,
                content={
                    "error": _error_code(exc),
                    "detail": "Retry later: concurrent update",
                },
            )
        safe = status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR
        return _json_error(status_code, exc, safe_detail=safe)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, handlers: list[IHTTPErrorHandler]) -> None:
        super().__init__(app)
        self.handlers = handlers

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            for handler in self.handlers:
                if handler.can_handle(exc):
                    return handler.handle(request, exc)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "INTERNAL_ERROR",
                    "detail": "Internal server error",
                },
            )
