"""
Financial Modeling Prep (FMP) service layer.

Provides tool-like functions that mirror the FMP MCP server capabilities:
  - get_income_statement
  - get_balance_sheet
  - get_cash_flow
  - get_company_profile
  - get_earnings
  - get_key_ratios

Uses httpx for async HTTP calls and a simple TTL cache to avoid repeated requests.
"""
import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/stable"
_CACHE: dict[str, tuple[float, Any]] = {}
_CACHE_TTL = int(os.getenv("FMP_CACHE_TTL", "300"))  # 5 minutes default


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


async def _fmp_request(endpoint: str, params: dict | None = None) -> Any:
    """Make authenticated request to FMP stable API. Returns empty list on errors."""
    api_key = _get_api_key()
    url = f"{FMP_BASE_URL}/{endpoint}"
    query_params = {"apikey": api_key}
    if params:
        query_params.update(params)

    cache_key = f"{endpoint}:{str(sorted(query_params.items()))}"
    cached = _cache_get(cache_key)
    if cached is not None:
        logger.debug("FMP cache hit: %s", endpoint)
        return cached

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=query_params)
        if response.status_code in (401, 402, 403):
            logger.warning(
                "FMP endpoint %s not available on current plan (HTTP %s)",
                endpoint,
                response.status_code,
            )
            return []
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()

    # FMP stable API wraps lists in {"value": [...], "Count": N}
    if isinstance(data, dict):
        if "Error Message" in data:
            logger.warning("FMP error for %s: %s", endpoint, data["Error Message"])
            return []
        if "value" in data:
            data = data["value"]

    _cache_set(cache_key, data)
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
