"""
Financial Modeling Prep (FMP) service layer.

Provides tool-like functions that mirror the FMP MCP server capabilities:
  - get_income_statement
  - get_balance_sheet
  - get_cash_flow
  - get_company_profile
  - get_earnings
  - get_key_ratios

Uses httpx for async HTTP calls and a two-tier cache (in-process TTL dict as L1,
optional Redis as L2) to avoid repeated requests. Redis is used only when
REDIS_URL is set and the redis package is installed; otherwise the L1 cache is
used alone with no behavioural change.
"""
import json
import logging
import os
import time
from typing import Any

import httpx

from app.cache.redis_client import get_redis

logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/stable"
_CACHE: dict[str, tuple[float, Any]] = {}
_CACHE_TTL = int(os.getenv("FMP_CACHE_TTL", "300"))  # 5 minutes default

# --------------------------------------------------------------------------- #
# Circuit breaker for the upstream FMP API.                                   #
# After _CB_THRESHOLD consecutive failures the breaker opens and requests are #
# short-circuited (returning empty) for _CB_COOLDOWN seconds, protecting the  #
# app from hammering a failing dependency and from cascading latency.         #
# --------------------------------------------------------------------------- #
_CB_THRESHOLD = int(os.getenv("FMP_CB_THRESHOLD", "5"))
_CB_COOLDOWN = float(os.getenv("FMP_CB_COOLDOWN", "30"))
_HTTP_TIMEOUT = float(os.getenv("FMP_HTTP_TIMEOUT", "30"))
_cb_failures = 0
_cb_opened_at = 0.0


def _circuit_open() -> bool:
    """True while the breaker is open (cooling down after repeated failures)."""
    global _cb_failures
    if _cb_failures < _CB_THRESHOLD:
        return False
    if time.time() - _cb_opened_at >= _CB_COOLDOWN:
        # Cooldown elapsed: half-open the breaker and allow a trial request.
        _cb_failures = 0
        return False
    return True


def _record_success() -> None:
    global _cb_failures
    _cb_failures = 0


def _record_failure() -> None:
    global _cb_failures, _cb_opened_at
    _cb_failures += 1
    if _cb_failures == _CB_THRESHOLD:
        _cb_opened_at = time.time()
        logger.warning(
            "FMP circuit breaker OPEN after %d consecutive failures; "
            "short-circuiting for %ss.",
            _CB_THRESHOLD,
            _CB_COOLDOWN,
        )


def _get_api_key() -> str:
    key = os.getenv("FMP_API_KEY")
    if not key:
        raise EnvironmentError(
            "FMP_API_KEY must be set in the environment to use Financial Intelligence."
        )
    return key


def _cache_get(key: str) -> Any | None:
    if key in _CACHE:
        ts, data = _CACHE[key]
        if time.time() - ts < _CACHE_TTL:
            return data
        del _CACHE[key]
    return None


def _cache_set(key: str, data: Any) -> None:
    _CACHE[key] = (time.time(), data)


async def _cache_get_async(key: str) -> Any | None:
    """Two-tier read: L1 in-memory, then L2 Redis."""
    hit = _cache_get(key)
    if hit is not None:
        return hit
    client = get_redis()
    if client is not None:
        try:
            raw = await client.get(key)
            if raw is not None:
                data = json.loads(raw)
                _cache_set(key, data)  # promote to L1
                return data
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            logger.debug("Redis get failed (%s); ignoring.", exc)
    return None


async def _cache_set_async(key: str, data: Any) -> None:
    """Two-tier write: L1 in-memory and, when available, L2 Redis with TTL."""
    _cache_set(key, data)
    client = get_redis()
    if client is not None:
        try:
            await client.set(key, json.dumps(data, default=str), ex=_CACHE_TTL)
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            logger.debug("Redis set failed (%s); ignoring.", exc)


async def _fmp_request(endpoint: str, params: dict | None = None) -> Any:
    """Make authenticated request to FMP stable API. Returns empty list on errors."""
    api_key = _get_api_key()
    url = f"{FMP_BASE_URL}/{endpoint}"
    query_params = {"apikey": api_key}
    if params:
        query_params.update(params)

    # Exclude the API key from the cache key so it is never persisted to Redis.
    safe_params = {k: v for k, v in query_params.items() if k != "apikey"}
    cache_key = f"fmp:{endpoint}:{str(sorted(safe_params.items()))}"
    cached = await _cache_get_async(cache_key)
    if cached is not None:
        logger.debug("FMP cache hit: %s", endpoint)
        return cached

    # Circuit breaker: if the upstream API has been failing, fail fast instead
    # of piling up slow requests against a known-bad dependency.
    if _circuit_open():
        logger.warning("FMP circuit open; skipping request to %s", endpoint)
        return []

    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            response = await client.get(url, params=query_params)
            if response.status_code in (401, 402, 403):
                logger.warning(
                    "FMP endpoint %s not available on current plan (HTTP %s)",
                    endpoint,
                    response.status_code,
                )
                # Auth/plan limits are not transient failures: don't trip the breaker.
                return []
            if response.status_code == 404:
                return []
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, httpx.TimeoutException) as exc:
        _record_failure()
        logger.warning("FMP request to %s failed (%s)", endpoint, exc)
        return []

    _record_success()

    # FMP stable API wraps lists in {"value": [...], "Count": N}
    if isinstance(data, dict):
        if "Error Message" in data:
            logger.warning("FMP error for %s: %s", endpoint, data["Error Message"])
            return []
        if "value" in data:
            data = data["value"]

    await _cache_set_async(cache_key, data)
    return data


async def get_company_profile(symbol: str) -> dict[str, Any]:
    """Get company profile including description, sector, market cap, etc."""
    data = await _fmp_request("profile", params={"symbol": symbol.upper()})
    if isinstance(data, list) and data:
        return data[0]
    return data if isinstance(data, dict) else {}


async def get_income_statement(symbol: str, period: str = "annual", limit: int = 4) -> list[dict]:
    """Get income statements (annual or quarter)."""
    data = await _fmp_request(
        "income-statement",
        params={"symbol": symbol.upper(), "period": period, "limit": str(limit)},
    )
    return data if isinstance(data, list) else []


async def get_balance_sheet(symbol: str, period: str = "annual", limit: int = 4) -> list[dict]:
    """Get balance sheet statements."""
    data = await _fmp_request(
        "balance-sheet-statement",
        params={"symbol": symbol.upper(), "period": period, "limit": str(limit)},
    )
    return data if isinstance(data, list) else []


async def get_cash_flow(symbol: str, period: str = "annual", limit: int = 4) -> list[dict]:
    """Get cash flow statements."""
    data = await _fmp_request(
        "cash-flow-statement",
        params={"symbol": symbol.upper(), "period": period, "limit": str(limit)},
    )
    return data if isinstance(data, list) else []


async def get_earnings(symbol: str, limit: int = 8) -> list[dict]:
    """Get historical earnings (EPS actual vs estimated)."""
    data = await _fmp_request(
        "earnings",
        params={"symbol": symbol.upper(), "limit": str(limit)},
    )
    return data if isinstance(data, list) else []


async def get_key_ratios(symbol: str, period: str = "annual", limit: int = 4) -> list[dict]:
    """Get key financial ratios."""
    data = await _fmp_request(
        "ratios",
        params={"symbol": symbol.upper(), "period": period, "limit": str(limit)},
    )
    return data if isinstance(data, list) else []


async def search_company(query: str) -> list[dict]:
    """Search for companies by name or ticker."""
    data = await _fmp_request("search-symbol", params={"query": query, "limit": "5"})
    return data if isinstance(data, list) else []


async def gather_all_financials(symbol: str) -> dict[str, Any]:
    """Gather all financial data for a symbol in one call."""
    profile = await get_company_profile(symbol)
    income = await get_income_statement(symbol, period="annual", limit=3)
    balance = await get_balance_sheet(symbol, period="annual", limit=3)
    cash_flow = await get_cash_flow(symbol, period="annual", limit=3)
    earnings = await get_earnings(symbol, limit=8)
    ratios = await get_key_ratios(symbol, period="annual", limit=3)

    return {
        "symbol": symbol.upper(),
        "profile": profile,
        "income_statements": income,
        "balance_sheets": balance,
        "cash_flow_statements": cash_flow,
        "earnings": earnings,
        "ratios": ratios,
    }
