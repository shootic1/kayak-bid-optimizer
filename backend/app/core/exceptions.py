"""Application exception types and global exception handlers.

Provides a small domain exception hierarchy plus handlers that translate any
raised error into a consistent JSON envelope. Centralising this keeps route
handlers free of repetitive try/except boilerplate and guarantees clients always
receive the same error shape.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger("app.exceptions")


class AppError(Exception):
    """Base class for all expected, domain-level application errors.

    Raising an ``AppError`` (or subclass) results in a structured JSON response
    with the given ``status_code`` and machine-readable ``code``.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "The requested resource was not found."


class ServiceUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "service_unavailable"
    message = "A required dependency is currently unavailable."


def _error_body(
    *, code: str, message: str, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build the canonical error response envelope."""
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI application."""

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        logger.warning("app_error", code=exc.code, status_code=exc.status_code, message=exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(code=exc.code, message=exc.message, details=exc.details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = "not_found" if exc.status_code == status.HTTP_404_NOT_FOUND else "http_error"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(code=code, message=str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                code="validation_error",
                message="Request validation failed.",
                details={"errors": exc.errors()},
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        # Never leak internal details to the client; log the full context.
        logger.error("unhandled_exception", error=str(exc), exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(code="internal_error", message="An unexpected error occurred."),
        )
