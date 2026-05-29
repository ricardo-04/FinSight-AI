"""
FinSight AI — MCP Server

Exposes FinSight's financial analysis capabilities as MCP tools,
usable from VS Code Copilot Chat, Claude Desktop, or any MCP client.

Tools:
  - search_documents: Semantic search over ingested financial documents
  - get_company_financials: Company profile + key financial data via FMP
  - extract_metrics: Extract structured metrics from raw text
  - fetch_sec_filing: Fetch SEC filings (10-K, 10-Q, 8-K) by ticker

Run:  python mcp_server.py
"""

import asyncio
import json
import os
import sys

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "FinSight AI",
    instructions=(
        "Financial analysis toolkit. Use search_documents to find information in "
        "uploaded earnings reports and filings. Use get_company_financials for live "
        "market data. Use extract_metrics to pull structured data from text. "
        "Use fetch_sec_filing to retrieve SEC filings."
    ),
)


@mcp.tool()
async def search_documents(query: str, top_k: int = 5) -> str:
    """Search ingested financial documents (earnings reports, filings, presentations) for relevant information.

    Args:
        query: Natural language search query, e.g. "Apple revenue Q1 2026"
        top_k: Maximum number of results to return (default 5)

    Returns:
        JSON array of matching document chunks with text, scores, and source info.
    """
    from app.tools.vector_search import vector_search

    results = await vector_search(query=query, top_k=top_k)
    if not results:
        return "No relevant documents found. Make sure documents have been uploaded and ingested."
    return json.dumps(results, indent=2, default=str)


@mcp.tool()
async def get_company_financials(ticker: str) -> str:
    """Get comprehensive financial data for a company: profile, income statement, balance sheet, ratios.

    Args:
        ticker: Stock ticker symbol, e.g. "AAPL", "MSFT", "NVDA"

    Returns:
        JSON object with company profile, latest income statement, and key ratios.
    """
    from app.services.fmp_service import (
        get_company_profile,
        get_income_statement,
        get_key_ratios,
    )

    profile = await get_company_profile(ticker)
    income = await get_income_statement(ticker, limit=1)
    ratios = await get_key_ratios(ticker, limit=1)

    result = {
        "profile": profile[0] if profile else {},
        "income_statement": income[0] if income else {},
        "key_ratios": ratios[0] if ratios else {},
    }
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def extract_metrics(text: str) -> str:
    """Extract structured financial metrics from raw text (earnings report, filing excerpt, etc.).

    Args:
        text: Raw text from a financial document. Can be a paragraph or multiple pages.

    Returns:
        JSON object with extracted fields: company, quarter, revenue, growth, guidance, risks.
    """
    from app.agents.extraction_agent import run_extraction

    metrics = await run_extraction(text)
    return json.dumps(metrics.model_dump(), indent=2)


@mcp.tool()
async def fetch_sec_filing(ticker: str, form_type: str = "10-K") -> str:
    """Fetch the most recent SEC filing for a company.

    Args:
        ticker: Stock ticker symbol, e.g. "AAPL"
        form_type: SEC form type — "10-K" (annual), "10-Q" (quarterly), "8-K" (current events)

    Returns:
        The text content of the filing (truncated to 50k chars).
    """
    from app.tools.sec_fetch import fetch_sec_filing as _fetch

    text = await _fetch(ticker=ticker, form_type=form_type)
    return text


if __name__ == "__main__":
    mcp.run()
