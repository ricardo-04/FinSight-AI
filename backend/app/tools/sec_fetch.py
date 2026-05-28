"""Fetch SEC filings by ticker and form type via the EDGAR full-text search API."""

import logging

import httpx

logger = logging.getLogger(__name__)

_EDGAR_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
_EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
_USER_AGENT = "FinSightAI/0.1 (research-tool)"


async def _resolve_cik(ticker: str) -> str | None:
    """Resolve a ticker symbol to a CIK number using the EDGAR company tickers JSON."""
    url = "https://www.sec.gov/files/company_tickers.json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"User-Agent": _USER_AGENT}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    ticker_upper = ticker.upper()
    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker_upper:
            return str(entry["cik_str"]).zfill(10)
    return None


async def fetch_sec_filing(ticker: str, form_type: str = "10-K") -> str:
    """Fetch the most recent SEC filing of *form_type* for *ticker*.

    Args:
        ticker: Stock ticker symbol (e.g. "AAPL").
        form_type: SEC form type (default "10-K"). Common values:
            10-K, 10-Q, 8-K, DEF 14A.

    Returns:
        The full text content of the filing, truncated to 50 000 characters.

    Raises:
        ValueError: If the ticker cannot be resolved or no filings found.
        RuntimeError: If the SEC API returns an unexpected error.
    """
    cik = await _resolve_cik(ticker)
    if not cik:
        raise ValueError(f"Could not resolve ticker '{ticker}' to a CIK number.")

    logger.info("Resolved %s -> CIK %s", ticker, cik)

    # Fetch recent submissions for this company
    submissions_url = _EDGAR_SUBMISSIONS_URL.format(cik=cik)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            submissions_url,
            headers={"User-Agent": _USER_AGENT},
            timeout=15,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"SEC EDGAR returned status {resp.status_code} for CIK {cik}."
            )
        submissions = resp.json()

    # Find the most recent filing of the requested form type
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession_numbers = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    target_idx: int | None = None
    for i, form in enumerate(forms):
        if form.upper() == form_type.upper():
            target_idx = i
            break

    if target_idx is None:
        raise ValueError(
            f"No '{form_type}' filing found for {ticker} (CIK {cik})."
        )

    accession = accession_numbers[target_idx].replace("-", "")
    primary_doc = primary_docs[target_idx]
    filing_url = (
        f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession}/{primary_doc}"
    )

    logger.info("Fetching filing: %s", filing_url)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            filing_url,
            headers={"User-Agent": _USER_AGENT},
            timeout=30,
            follow_redirects=True,
        )
        resp.raise_for_status()

    # Return plain text, truncated to a reasonable size for LLM consumption
    text = resp.text[:50_000]
    logger.info(
        "Fetched SEC filing: ticker=%s form=%s chars=%d", ticker, form_type, len(text)
    )
    return text
