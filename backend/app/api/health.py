"""
Health check endpoints.

Three levels, following the Kubernetes probe convention:

- ``GET /health/``        — alias to /live, for backwards compat.
- ``GET /health/live``    — liveness: the process is running and the event loop
  is responsive. Used by the container orchestrator to decide if it should
  *restart* the container. Never touches the DB or external services; it must
  not fail due to dependency problems.
- ``GET /health/ready``   — readiness: the app can actually serve traffic. Checks
  the DB and (when configured) Redis. Used by load-balancers to decide if this
  instance should *receive requests*. Returns 503 if any dependency is unhealthy.
"""
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
@router.get("/live")
async def liveness():
    """Liveness probe — always 200 if the event loop is running."""
    return {"status": "ok", "service": "finsight-ai"}


@router.get("/ready")
async def readiness():
    """Readiness probe — 200 only when DB and optional Redis are reachable."""
    checks: dict[str, str] = {}
    healthy = True

    # --- Database -----------------------------------------------------------
    try:
        from sqlalchemy import text

        from app.db.session import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Readiness: DB check failed: %s", exc)
        checks["db"] = f"error: {exc}"
        healthy = False

    # --- Redis (optional) ---------------------------------------------------
    from app.cache.redis_client import get_redis, redis_configured

    if redis_configured():
        client = get_redis()
        if client is not None:
            try:
                await client.ping()
                checks["redis"] = "ok"
            except Exception as exc:  # noqa: BLE001
                logger.warning("Readiness: Redis check failed: %s", exc)
                checks["redis"] = f"error: {exc}"
                # Redis is optional (conversation store degrades gracefully),
                # so a Redis failure does not mark the instance un-ready.
        else:
            checks["redis"] = "unavailable (client init failed)"
    else:
        checks["redis"] = "not configured"

    status_code = 200 if healthy else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if healthy else "degraded", "checks": checks},
    )

