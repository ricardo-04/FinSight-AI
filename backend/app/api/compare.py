import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.comparison_agent import (
    ComparisonResult,
    DocumentMetrics,
    run_comparison,
)
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()


class CompareRequest(BaseModel):
    document_ids: list[str] = Field(
        min_length=2, description="List of 2+ document UUIDs to compare"
    )


class CompareResponse(BaseModel):
    documents: list[DocumentMetrics]
    analysis: str


@router.post("/", response_model=CompareResponse)
async def compare(request: CompareRequest) -> CompareResponse:
    """Compare financial metrics across two or more documents.

    Args:
        request: Contains the list of document UUIDs to compare.

    Returns:
        CompareResponse with per-document metrics and a comparative analysis.

    Raises:
        400: If fewer than 2 document IDs are provided.
        500: If the LLM fails after retries.
    """
    if len(request.document_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 document IDs are required for comparison.",
        )

    logger.info("Compare request: document_ids=%s", request.document_ids)

    async with AsyncSessionLocal() as session:
        try:
            result: ComparisonResult = await run_comparison(
                document_ids=request.document_ids,
                session=session,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except RuntimeError as exc:
            logger.error("Compare failed: %s", exc)
            raise HTTPException(
                status_code=500,
                detail="Failed to generate comparison. Please try again.",
            ) from exc

    return CompareResponse(documents=result.documents, analysis=result.analysis)
