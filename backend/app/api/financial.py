"""
Financial Intelligence API endpoint.

Provides a POST endpoint to analyze a company by ticker or name,
returning structured financial data and an AI-generated report.
"""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.financial_agent import (
    CompanyOverview,
    FinancialAnalysisResult,
    FinancialHighlights,
    run_financial_analysis,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class FinancialAnalysisRequest(BaseModel):
    query: str = Field(
        description="Company name (e.g. 'Apple') or ticker symbol (e.g. 'AAPL')"
    )


class FinancialAnalysisResponse(BaseModel):
    overview: CompanyOverview
    highlights: FinancialHighlights
    report: str


@router.post("/analyze", response_model=FinancialAnalysisResponse)
async def analyze_company(request: FinancialAnalysisRequest) -> FinancialAnalysisResponse:
    """Analyze a company's financials and generate an AI investment report.

    Args:
        request: Contains the company name or ticker to analyze.

    Returns:
        FinancialAnalysisResponse with overview, key metrics, and report.

    Raises:
        400: If query is empty or company not found.
        500: If analysis fails.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    logger.info("Financial analysis request: query='%s'", request.query)

    try:
        result: FinancialAnalysisResult = await run_financial_analysis(request.query.strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Financial analysis failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate financial analysis. Please try again.",
        ) from exc

    return FinancialAnalysisResponse(
        overview=result.overview,
        highlights=result.highlights,
        report=result.report,
    )
