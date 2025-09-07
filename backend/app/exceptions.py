import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app")

class AppException(Exception):
    """Domain-level errors with explicit status codes & machine codes."""
    def __init__(self, *, code: str, message: str, status_code: int = 400, details: Optional[Any] = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

def _error_payload(
    *,
    request: Request,
    code: str,
    message: str,
    status_code: int,
    details: Optional[Any] = None,
) -> JSONResponse:
    rid = getattr(getattr(request, "state", None), "request_id", "-")
    body: Dict[str, Any] = {
        "status": "error",
        "code": code,
        "message": message,
        "details": details,
        "request_id": rid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(status_code=status_code, content=body)

def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exc(request: Request, exc: AppException):
        logger.warning("AppException: %s", exc.message, extra={"path": request.url.path, "method": request.method})
        return _error_payload(
            request=request,
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exc(request: Request, exc: StarletteHTTPException):
        # Normalize to our error envelope
        logger.info(
            "HTTPException: %s",
            exc.detail,
            extra={"path": request.url.path, "method": request.method, "status_code": exc.status_code},
        )
        return _error_payload(
            request=request,
            code="http_error",
            message=str(exc.detail),
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exc(request: Request, exc: RequestValidationError):
        logger.info("Validation error", extra={"path": request.url.path, "method": request.method})
        return _error_payload(
            request=request,
            code="validation_error",
            message="Invalid request.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exc(request: Request, exc: Exception):
        logger.exception("Unhandled error", extra={"path": request.url.path, "method": request.method})
        return _error_payload(
            request=request,
            code="internal_server_error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
