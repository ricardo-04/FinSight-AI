"""
Shared async Redis client.

A single process-wide Redis connection pool is shared by every component that
needs L2 caching or durable cross-replica state (FMP cache, conversation memory,
rate limiting). Redis is **optional**: when ``REDIS_URL`` is unset or the server
is unreachable, :func:`get_redis` returns ``None`` and callers degrade gracefully
to in-process behaviour.

Two client flavours are exposed:
  - :func:`get_redis`       -> ``decode_responses=True`` (str values; JSON caches).
  - :func:`get_redis_bytes` -> ``decode_responses=False`` (raw bytes; e.g. the
    PydanticAI message serializer emits bytes).
"""
import logging
import os

logger = logging.getLogger(__name__)

_REDIS_URL = os.getenv("REDIS_URL", "").strip()

# Sentinel values: ``None`` means "not yet initialised"; ``False`` means
# "initialised and known-unavailable" so we never retry the import/connect.
_client_str = None
_client_bytes = None


def _build(decode_responses: bool):
    if not _REDIS_URL:
        return False
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(
            _REDIS_URL,
            encoding="utf-8",
            decode_responses=decode_responses,
        )
        logger.info(
            "Redis enabled (decode_responses=%s) at %s", decode_responses, _REDIS_URL
        )
        return client
    except Exception as exc:  # noqa: BLE001 - degrade gracefully
        logger.warning("Redis unavailable (%s); falling back to in-process state.", exc)
        return False


def get_redis():
    """Return the shared string-decoding Redis client, or None if unavailable."""
    global _client_str
    if _client_str is None:
        _client_str = _build(decode_responses=True)
    return _client_str or None


def get_redis_bytes():
    """Return the shared bytes Redis client, or None if unavailable."""
    global _client_bytes
    if _client_bytes is None:
        _client_bytes = _build(decode_responses=False)
    return _client_bytes or None


def redis_configured() -> bool:
    """True if a REDIS_URL is configured (independent of reachability)."""
    return bool(_REDIS_URL)
