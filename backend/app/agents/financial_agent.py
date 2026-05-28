"""
Financial Analysis Agent - generates investment insights from FMP data.

Flow:
  1. Receives a company ticker/name from the user.
  2. Uses the FMP service to gather financial data (income, balance sheet, etc.).
  3. Constructs a data context block for the LLM.
  4. Calls the LLM to produce a structured financial analysis report.

All LLM calls go through llm_provider.
"""
import logging
import os
from typing import Any

from opentelemetry import trace
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from app.services.fmp_service import gather_all_financials, search_company
from app.services.llm_provider import get_chat_model

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_MAX_RETRIES: int = int(os.getenv("FINANCIAL_AGENT_MAX_RETRIES", "2"))

_SYSTEM_PROMPT = """\
You are a senior financial analyst AI. You receive raw financial data about a company
and produce a comprehensive investment analysis report.

Your report MUST include all these sections:
1. **Company Overview** - Brief description, sector, market cap, employees
2. **Financial Performance** - Revenue trends, profitability, margins analysis
3. **Balance Sheet Health** - Assets, liabilities, debt levels, liquidity
4. **Cash Flow Analysis** - Operating cash flow trends, free cash flow, capex
5. **Earnings Track Record** - EPS trends, beats/misses history
6. **Key Ratios** - P/E, ROE, debt-to-equity, current ratio, etc.
7. **Growth & Trends** - Revenue growth rate, margin expansion/contraction
8. **Risk Factors** - Key risks based on the financial data
9. **Investment Insight** - Concise summary with bull/bear case

Rules:
- Use ONLY the provided data. Do not fabricate numbers.
- Format currency values clearly (e.g., $1.2B, $450M).
- Be objective and balanced - present both positives and negatives.
- Keep the total report concise but informative (aim for 600-900 words).
- Use bullet points for clarity where appropriate.
"""


class CompanyOverview(BaseModel):
    name: str = Field(description="Company name")
    symbol: str = Field(description="Ticker symbol")
    sector: str = Field(default="", description="Company sector")
    industry: str = Field(default="", description="Company industry")
    market_cap: str = Field(default="", description="Market capitalization formatted")
    description: str = Field(default="", description="Brief company description")


class FinancialHighlights(BaseModel):
    revenue_latest: str = Field(default="", description="Latest annual revenue")
    net_income_latest: str = Field(default="", description="Latest net income")
    revenue_growth: str = Field(default="", description="YoY revenue growth percentage")
    profit_margin: str = Field(default="", description="Net profit margin")
    debt_to_equity: str = Field(default="", description="Debt to equity ratio")
    current_ratio: str = Field(default="", description="Current ratio")
    roe: str = Field(default="", description="Return on equity")
    free_cash_flow: str = Field(default="", description="Free cash flow")


class FinancialAnalysisResult(BaseModel):
    """Structured output of the financial analysis agent."""
    overview: CompanyOverview
    highlights: FinancialHighlights
    report: str = Field(description="Full AI-generated analysis report in markdown")


_agent: Agent[None, FinancialAnalysisResult] | None = None


def _get_agent() -> "Agent[None, FinancialAnalysisResult]":
    """Lazily initialise the PydanticAI agent."""
    global _agent
    if _agent is None:
        _agent = Agent(
            model=get_chat_model(),
            output_type=FinancialAnalysisResult,
            system_prompt=_SYSTEM_PROMPT,
            retries=_MAX_RETRIES,
        )
    return _agent


def _format_currency(value: float | int | None) -> str:
    """Format large numbers into human-readable currency."""
    if value is None:
        return "N/A"
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    if abs_val >= 1_000_000_000_000:
        return f"{sign}${abs_val / 1_000_000_000_000:.2f}T"
    if abs_val >= 1_000_000_000:
        return f"{sign}${abs_val / 1_000_000_000:.2f}B"
    if abs_val >= 1_000_000:
        return f"{sign}${abs_val / 1_000_000:.1f}M"
    return f"{sign}${abs_val:,.0f}"


def _build_data_context(data: dict[str, Any]) -> str:
    """Format raw FMP data into a context block for the LLM."""
    sections: list[str] = []

    # Profile
    profile = data.get("profile", {})
    if profile:
        sections.append(
            f"## Company Profile\n"
            f"- Name: {profile.get('companyName', 'N/A')}\n"
            f"- Symbol: {data['symbol']}\n"
            f"- Sector: {profile.get('sector', 'N/A')}\n"
            f"- Industry: {profile.get('industry', 'N/A')}\n"
            f"- Market Cap: {_format_currency(profile.get('mktCap'))}\n"
            f"- Price: ${profile.get('price', 'N/A')}\n"
            f"- Employees: {profile.get('fullTimeEmployees', 'N/A')}\n"
            f"- Description: {profile.get('description', 'N/A')[:300]}"
        )

    # Income Statements
    income = data.get("income_statements", [])
    if income:
        lines = ["## Income Statements (Annual)"]
        for stmt in income[:3]:
            lines.append(
                f"- {stmt.get('date', 'N/A')}: Revenue={_format_currency(stmt.get('revenue'))}, "
                f"Net Income={_format_currency(stmt.get('netIncome'))}, "
                f"Gross Margin={_pct(stmt.get('grossProfitRatio'))}, "
                f"Net Margin={_pct(stmt.get('netIncomeRatio'))}, "
                f"EPS={stmt.get('eps', 'N/A')}"
            )
        sections.append("\n".join(lines))

    # Balance Sheets
    balance = data.get("balance_sheets", [])
    if balance:
        lines = ["## Balance Sheets (Annual)"]
        for stmt in balance[:3]:
            lines.append(
                f"- {stmt.get('date', 'N/A')}: Total Assets={_format_currency(stmt.get('totalAssets'))}, "
                f"Total Liabilities={_format_currency(stmt.get('totalLiabilities'))}, "
                f"Total Debt={_format_currency(stmt.get('totalDebt'))}, "
                f"Cash={_format_currency(stmt.get('cashAndCashEquivalents'))}, "
                f"Equity={_format_currency(stmt.get('totalStockholdersEquity'))}"
            )
        sections.append("\n".join(lines))

    # Cash Flow
    cash_flow = data.get("cash_flow_statements", [])
    if cash_flow:
        lines = ["## Cash Flow Statements (Annual)"]
        for stmt in cash_flow[:3]:
            lines.append(
                f"- {stmt.get('date', 'N/A')}: Operating CF={_format_currency(stmt.get('operatingCashFlow'))}, "
                f"CapEx={_format_currency(stmt.get('capitalExpenditure'))}, "
                f"Free CF={_format_currency(stmt.get('freeCashFlow'))}, "
                f"Dividends Paid={_format_currency(stmt.get('dividendsPaid'))}"
            )
        sections.append("\n".join(lines))

    # Earnings
    earnings = data.get("earnings", [])
    if earnings:
        lines = ["## Earnings History"]
        for e in earnings[:6]:
            lines.append(
                f"- {e.get('date', 'N/A')}: EPS Actual={e.get('eps', 'N/A')}, "
                f"EPS Estimated={e.get('epsEstimated', 'N/A')}, "
                f"Revenue={_format_currency(e.get('revenue'))}"
            )
        sections.append("\n".join(lines))

    # Ratios
    ratios = data.get("ratios", [])
    if ratios:
        latest = ratios[0]
        sections.append(
            f"## Key Ratios (Latest)\n"
            f"- P/E: {_round(latest.get('priceEarningsRatio'))}\n"
            f"- ROE: {_pct(latest.get('returnOnEquity'))}\n"
            f"- ROA: {_pct(latest.get('returnOnAssets'))}\n"
            f"- Debt/Equity: {_round(latest.get('debtEquityRatio'))}\n"
            f"- Current Ratio: {_round(latest.get('currentRatio'))}\n"
            f"- Gross Margin: {_pct(latest.get('grossProfitMargin'))}\n"
            f"- Net Margin: {_pct(latest.get('netProfitMargin'))}\n"
            f"- Dividend Yield: {_pct(latest.get('dividendYield'))}"
        )

    return "\n\n".join(sections)


def _pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%" if abs(value) < 1 else f"{value:.1f}%"


def _round(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}"


async def resolve_symbol(query: str) -> str | None:
    """Resolve a company name or ticker to a valid symbol."""
    # If it looks like a ticker already (all caps, short), use it directly
    if query.upper() == query and len(query) <= 5 and query.isalpha():
        return query.upper()

    # Search via FMP
    results = await search_company(query)
    if results:
        return results[0].get("symbol", "").upper()
    return None


async def run_financial_analysis(query: str) -> FinancialAnalysisResult:
    """Run a full financial analysis for the given company query.

    Args:
        query: Company name (e.g., "Apple") or ticker (e.g., "AAPL").

    Returns:
        FinancialAnalysisResult with overview, highlights, and full report.

    Raises:
        ValueError: If company cannot be found.
        RuntimeError: If LLM fails.
    """
    with tracer.start_as_current_span("financial_analysis") as span:
        span.set_attribute("query", query)

        # Resolve ticker
        symbol = await resolve_symbol(query)
        if not symbol:
            raise ValueError(f"Could not find a company matching '{query}'.")

        span.set_attribute("symbol", symbol)
        logger.info("Running financial analysis for %s (resolved from '%s')", symbol, query)

        # Gather data via FMP service (MCP tools)
        data = await gather_all_financials(symbol)

        if not data.get("profile") and not data.get("income_statements"):
            raise ValueError(f"No financial data found for symbol '{symbol}'. The symbol may be invalid or data may not be available.")

        # Build context for LLM
        context = _build_data_context(data)

        # Run agent
        agent = _get_agent()
        prompt = (
            f"Analyze the following financial data for {symbol} and produce a complete "
            f"investment analysis report.\n\n{context}"
        )

        result = await agent.run(prompt)
        return result.output
