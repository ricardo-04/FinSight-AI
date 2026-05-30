"""
Optional API-key authentication.

Auth is opt-in: if the ``API_KEY`` environment variable is unset or empty, all
requests pass through (convenient for local dev). When ``API_KEY`` is set, every
request to a protected route must present a matching ``X-API-Key`` header.

Health checks and the OpenAPI docs remain public so liveness probes and the
Swagger UI keep working.
"""
import hmac
import logging
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

_PUBLIC_PATH_PREFIXES: tuple[str, ...] = (
    "/health",   # covers /health/, /health/live, /health/ready
    "/docs",
    "/openapi.json",
    "/redoc",
)


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Reject requests without a valid ``X-API-Key`` when an API key is configured."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self._api_key = os.getenv("API_KEY", "").strip()
        if self._api_key:
            logger.info("API key authentication is ENABLED.")
        else:
            logger.info("API key authentication is DISABLED (no API_KEY set).")

    async def dispatch(self, request: Request, call_next):
        if not self._api_key:
            return await call_next(request)

        path = request.url.path
        if request.method == "OPTIONS" or any(
            path.startswith(prefix) for prefix in _PUBLIC_PATH_PREFIXES
        ):
            return await call_next(request)

        provided = request.headers.get("X-API-Key", "")
        # Constant-time comparison to avoid timing side channels.
        if not hmac.compare_digest(provided, self._api_key):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid API key."},
            )

        return await call_next(request)
