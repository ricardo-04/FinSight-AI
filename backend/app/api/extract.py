import logging
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.agents.extraction_agent import FinancialMetrics, run_extraction
from app.db.session import AsyncSessionLocal
from app.models.document import DocumentChunk
from app.services.document_service import get_document

logger = logging.getLogger(__name__)

router = APIRouter()

# Keywords that signal a chunk contains the financial statements we extract from.
# Long filings (e.g. SEC 10-Q/10-K) open with pages of legal boilerplate, so the
# income statement often sits past a naive "first N characters" cutoff. We float
# the highest-signal chunks to the front before truncation so the revenue and
# earnings tables actually reach the model.
_FINANCIAL_KEYWORDS: tuple[str, ...] = (
    "total revenues",
    "total revenue",
    "revenue",
    "net earnings",
    "net income",
    "operating income",
    "gross profit",
    "earnings per share",
    "income statement",
    "statements of operations",
)


def _financial_score(text: str) -> int:
    """Count financial-statement keyword hits in a chunk (case-insensitive)."""
    lowered = text.lower()
    return sum(lowered.count(keyword) for keyword in _FINANCIAL_KEYWORDS)


def _prioritize_chunks(chunk_texts: list[str]) -> str:
    """Order chunks so financial-statement content sits near the front.

    Keeps the first chunk first (cover page -> company name + reporting period),
    then places the remaining chunks with the most financial-statement signal
    ahead of the rest. The caller still truncates to a token budget, so this
    ensures the revenue/earnings tables survive the cut.
    """
    if len(chunk_texts) <= 1:
        return "\n\n".join(chunk_texts)

    head, rest = chunk_texts[0], chunk_texts[1:]
    indexed = list(enumerate(rest))
    # Stable sort: higher financial score first, original order breaks ties.
    indexed.sort(key=lambda pair: (-_financial_score(pair[1]), pair[0]))
    ordered = [head] + [text for _, text in indexed]
    return "\n\n".join(ordered)


class ExtractionResponse(BaseModel):
    document_id: str
    filename: str
    metrics: FinancialMetrics


@router.post("/{document_id}", response_model=ExtractionResponse)
async def extract_metrics(document_id: str) -> ExtractionResponse:
    """Run the extraction agent over all chunks of a document.

    Concatenates the stored chunks and sends them to the extraction agent,
    which returns structured FinancialMetrics validated by Pydantic.

    Args:
        document_id: UUID of a previously uploaded document.

    Returns:
        ExtractionResponse with document metadata and extracted metrics.

    Raises:
        404: If the document does not exist.
        422: If the document has no ingested chunks.
        500: If the LLM extraction fails after retries.
    """
    async with AsyncSessionLocal() as session:
        try:
            doc_meta = await get_document(document_id, session)
        except ValueError:
            raise HTTPException(
                status_code=404,
                detail=f"Document '{document_id}' not found.",
            )

        stmt = (
            select(DocumentChunk.text)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        result = await session.execute(stmt)
        chunk_texts: list[str] = [row.text for row in result.fetchall()]

    if not chunk_texts:
        raise HTTPException(
            status_code=422,
            detail=f"Document '{document_id}' has no ingested chunks. Re-upload the file.",
        )

    full_text = _prioritize_chunks(chunk_texts)
    extraction_budget = int(os.getenv("EXTRACTION_MAX_INPUT_LENGTH", "16000"))
    logger.info(
        "Running extraction: document_id=%s chunks=%d budget=%d",
        document_id,
        len(chunk_texts),
        extraction_budget,
    )

    try:
        metrics = await run_extraction(full_text, max_length=extraction_budget)
    except RuntimeError as exc:
        logger.error("Extraction failed for document_id=%s: %s", document_id, exc)
        raise HTTPException(status_code=500, detail="Metric extraction failed. Please try again.") from exc

    return ExtractionResponse(
        document_id=document_id,
        filename=doc_meta["filename"],
        metrics=metrics,
    )
