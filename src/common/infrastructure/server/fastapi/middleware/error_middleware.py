from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import ClassVar

from common.application.exceptions import (
    ApplicationError,
    DuplicateEntryError,
    NotFoundError,
    OptimisticLockError,
    RepositoryError,
)
from common.domain.exceptions import DomainError
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class IHTTPErrorHandler(ABC):
    @abstractmethod
    def can_handle(self, exc: Exception) -> bool: ...

    @abstractmethod
    def handle(self, request: Request, exc: Exception) -> JSONResponse: ...


class DomainErrorHandler(IHTTPErrorHandler):
    def can_handle(self, exc: Exception) -> bool:
        return isinstance(exc, DomainError)

    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": type(exc).__name__, "detail": str(exc)},
        )


class ApplicationErrorHandler(IHTTPErrorHandler):
    ERROR_STATUS_MAP: ClassVar[dict[type[Exception], int]] = {
        NotFoundError: status.HTTP_404_NOT_FOUND
    }

    def can_handle(self, exc: Exception) -> bool:
        return isinstance(exc, ApplicationError)

    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        status_code = self.ERROR_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(
            status_code=status_code,
            content={"error": type(exc).__name__, "detail": str(exc)},
        )


class RepositoryErrorHandler(IHTTPErrorHandler):
    ERROR_STATUS_MAP: ClassVar[dict[type[Exception], int]] = {
        DuplicateEntryError: status.HTTP_409_CONFLICT,
        OptimisticLockError: status.HTTP_409_CONFLICT,
    }

    def can_handle(self, exc: Exception) -> bool:
        return isinstance(exc, RepositoryError)

    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, OptimisticLockError):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "OptimisticLockError",
                    "detail": f"Retry later: {exc!s}",
                },
            )

        status_code = self.ERROR_STATUS_MAP.get(
            type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "error": type(exc).__name__,
                "detail": str(exc),
            },
        )


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, handlers: list[IHTTPErrorHandler]):
        super().__init__(app)
        self.handlers = handlers

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            for handler in self.handlers:
                if handler.can_handle(exc):
                    return handler.handle(request, exc)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "InternalError", "detail": str(exc)},
            )
