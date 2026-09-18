"""
Centralized exception classes and FastAPI exception handlers.

All application-specific exceptions inherit from DarukaaError.
Exception handlers translate these into structured JSON responses.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------------


class DarukaaError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, status_code: int = 500, detail: Any = None) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class NotFoundError(DarukaaError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str | None = None) -> None:
        msg = f"{resource} not found"
        if identifier:
            msg = f"{resource} '{identifier}' not found"
        super().__init__(message=msg, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(DarukaaError):
    """Resource already exists or conflicts."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class AuthenticationError(DarukaaError):
    """Authentication failed."""

    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(DarukaaError):
    """Insufficient permissions."""

    def __init__(self, message: str = "Not authorized to perform this action") -> None:
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class ValidationError(DarukaaError):
    """Input validation failed."""

    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class GeospatialValidationError(ValidationError):
    """Geospatial-specific validation failure."""

    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(message=f"Geospatial validation error: {message}", detail=detail)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


async def darukaa_error_handler(_request: Request, exc: DarukaaError) -> JSONResponse:
    """Handle all DarukaaError subclasses with a structured JSON response."""
    body: dict[str, Any] = {"error": exc.message}
    if exc.detail is not None:
        body["detail"] = exc.detail
    return JSONResponse(status_code=exc.status_code, content=body)


async def generic_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Catch-all handler — prevents leaking internal details in production."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An unexpected error occurred"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application instance."""
    app.add_exception_handler(DarukaaError, darukaa_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_error_handler)
