"""Request logging middleware using structlog."""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all incoming requests with timing and context."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Clear any existing context and bind request info
        structlog.contextvars.clear_contextvars()

        # Get or generate request ID for tracing
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Bind context that will appear in all logs during this request
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log successful request
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add request ID to response headers for client-side tracing
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log failed request with exception info
            logger.exception(
                "Request failed",
                duration_ms=round(duration_ms, 2),
                error_type=type(exc).__name__,
            )
            raise
