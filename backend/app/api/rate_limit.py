"""
Request rate limiting middleware.

A fixed-window limiter caps how many requests a single client may make per
window. Clients are identified by their API key (``X-API-Key``) when present,
otherwise by source IP. The limiter is **distributed-aware**: when Redis is
configured it uses an atomic ``INCR`` + ``EXPIRE`` counter shared across
replicas; otherwise it falls back to an in-process counter (correct for a single
instance, best-effort across many).

Disabled by default for local dev. Enable by setting ``RATE_LIMIT_REQUESTS`` to
a positive integer. Health and docs paths are always exempt so probes and the
Swagger UI keep working.
"""
import logging
import os
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.cache.redis_client import get_redis

logger = logging.getLogger(__name__)

_LIMIT: int = int(os.getenv("RATE_LIMIT_REQUESTS", "0"))  # 0 disables limiting
_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
_KEY_PREFIX = "ratelimit:"

_EXEMPT_PREFIXES: tuple[str, ...] = ("/health", "/docs", "/openapi.json", "/redoc")

# In-process fallback: {client_key: (window_start_epoch, count)}
_local: dict[str, tuple[float, int]] = {}


def _client_id(request: Request) -> str:
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"key:{api_key}"
    client = request.client
    return f"ip:{client.host if client else 'unknown'}"


def _local_increment(client_key: str) -> int:
    now = time.time()
    window_start, count = _local.get(client_key, (now, 0))
    if now - window_start >= _WINDOW:
        window_start, count = now, 0
    count += 1
    _local[client_key] = (window_start, count)
    return count


async def _redis_increment(client_key: str) -> int | None:
    client = get_redis()
    if client is None:
        return None
    try:
        redis_key = _KEY_PREFIX + client_key
        count = await client.incr(redis_key)
        if count == 1:
            await client.expire(redis_key, _WINDOW)
        return int(count)
    except Exception as exc:  # noqa: BLE001 - degrade gracefully
        logger.debug("Rate-limit Redis op failed (%s); using in-process counter.", exc)
        return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests once a client exceeds the configured per-window quota."""

    def __init__(self, app) -> None:
        super().__init__(app)
        if _LIMIT > 0:
            logger.info(
                "Rate limiting ENABLED: %d requests / %ds per client.", _LIMIT, _WINDOW
            )
        else:
            logger.info("Rate limiting DISABLED (RATE_LIMIT_REQUESTS not set).")

    async def dispatch(self, request: Request, call_next):
        if _LIMIT <= 0 or request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        if any(path.startswith(prefix) for prefix in _EXEMPT_PREFIXES):
            return await call_next(request)

        client_key = _client_id(request)
        count = await _redis_increment(client_key)
        if count is None:
            count = _local_increment(client_key)

        if count > _LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please slow down."},
                headers={"Retry-After": str(_WINDOW)},
            )

        return await call_next(request)
