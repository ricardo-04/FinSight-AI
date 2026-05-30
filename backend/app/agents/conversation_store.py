"""
Conversation memory store for the analyst agent.

Keeps recent message history per ``conversation_id`` so the agent has memory of
earlier turns within a session.

Two tiers, transparently selected:
  - **Redis** (when ``REDIS_URL`` is set and reachable): durable across restarts
    and shared across replicas. Histories are serialized with PydanticAI's
    ``ModelMessagesTypeAdapter`` and stored under a TTL so abandoned sessions are
    reclaimed automatically.
  - **In-process dict** (fallback): a simple LRU-bounded map used for local dev
    or when Redis is unavailable. Not durable and not shared across replicas.

A per-conversation cap bounds history growth so prompts stay within context
limits; the oldest messages are dropped first.
"""
import logging
import os
import threading
import uuid

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter

from app.cache.redis_client import get_redis_bytes

logger = logging.getLogger(__name__)

# Maximum number of stored messages per conversation (system/user/tool/response
# entries combined). Oldest are evicted first.
_MAX_MESSAGES: int = int(os.getenv("CONVERSATION_MAX_MESSAGES", "40"))
# Maximum number of concurrent conversations retained in the in-process fallback
# before the least-recently-used ones are evicted, to bound total memory.
_MAX_CONVERSATIONS: int = int(os.getenv("CONVERSATION_MAX_SESSIONS", "200"))
# TTL (seconds) for Redis-backed conversations; abandoned sessions expire.
_TTL_SECONDS: int = int(os.getenv("CONVERSATION_TTL_SECONDS", str(60 * 60 * 24)))
_KEY_PREFIX = "conversation:"

_store: "dict[str, list[ModelMessage]]" = {}
_lock = threading.Lock()


def new_conversation_id() -> str:
    """Return a fresh unique conversation identifier."""
    return uuid.uuid4().hex


def _trim(messages: list[ModelMessage]) -> list[ModelMessage]:
    return messages[-_MAX_MESSAGES:] if len(messages) > _MAX_MESSAGES else list(messages)


async def get_history(conversation_id: str | None) -> list[ModelMessage] | None:
    """Return stored messages for *conversation_id*, or None if unknown/empty."""
    if not conversation_id:
        return None

    client = get_redis_bytes()
    if client is not None:
        try:
            raw = await client.get(_KEY_PREFIX + conversation_id)
            if raw:
                return list(ModelMessagesTypeAdapter.validate_json(raw))
            return None
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            logger.warning("Redis history read failed (%s); using in-process store.", exc)

    with _lock:
        history = _store.get(conversation_id)
        return list(history) if history else None


async def save_history(conversation_id: str, messages: list[ModelMessage]) -> None:
    """Persist *messages* for *conversation_id*, applying size caps and TTL."""
    if not conversation_id:
        return
    trimmed = _trim(messages)

    client = get_redis_bytes()
    if client is not None:
        try:
            payload = ModelMessagesTypeAdapter.dump_json(trimmed)
            await client.set(_KEY_PREFIX + conversation_id, payload, ex=_TTL_SECONDS)
            return
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            logger.warning("Redis history write failed (%s); using in-process store.", exc)

    with _lock:
        if conversation_id not in _store and len(_store) >= _MAX_CONVERSATIONS:
            # Evict the oldest conversation (first inserted) to bound memory.
            oldest = next(iter(_store))
            _store.pop(oldest, None)
        _store[conversation_id] = trimmed


async def clear(conversation_id: str) -> None:
    """Forget a conversation's history."""
    if not conversation_id:
        return
    client = get_redis_bytes()
    if client is not None:
        try:
            await client.delete(_KEY_PREFIX + conversation_id)
            return
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            logger.warning("Redis history delete failed (%s); using in-process store.", exc)
    with _lock:
        _store.pop(conversation_id, None)
