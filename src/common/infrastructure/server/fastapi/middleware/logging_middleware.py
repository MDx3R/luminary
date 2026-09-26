import logging
import time
import traceback
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, logger: logging.Logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        extra: dict[str, Any] = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path_params": request.path_params,
            "query_params": dict(request.query_params),
        }

        self.logger.info("incoming request", extra={"extra": extra})

        try:
            response: Response = await call_next(request)
        except Exception:
            # NOTE: Normally shouldn't be invoked
            process_time = (time.time() - start_time) * 1000
            extra.update(
                {
                    "process_time_ms": f"{process_time:.2f}",
                }
            )

            self.logger.exception(
                "request failed",
                extra={"extra": extra},
            )
            raise

        process_time = (time.time() - start_time) * 1000
        if response.status_code >= status.HTTP_400_BAD_REQUEST:
            extra.update(
                {
                    "status_code": response.status_code,
                    "process_time_ms": f"{process_time:.2f}",
                }
            )
            self.logger.error(
                "request completed with error status",
                extra={"extra": extra},
            )
            return response

        extra.update(
            {
                "status_code": response.status_code,
                "process_time_ms": f"{process_time:.2f}",
            }
        )
        self.logger.info("request completed successfully", extra={"extra": extra})
        return response


class TraceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, logger: logging.Logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            response: Response = await call_next(request)
            trace = traceback.format_tb(None)
            self.logger.debug(f"request trace:\n{trace}")
        except Exception:
            exc_tb = traceback.format_exc()
            self.logger.debug(f"request failed:\n{exc_tb}")
            raise

        return response
