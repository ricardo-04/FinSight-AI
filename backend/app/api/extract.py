import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.agents.extraction_agent import FinancialMetrics, run_extraction
from app.db.session import AsyncSessionLocal
from app.models.document import DocumentChunk
from app.services.document_service import get_document

logger = logging.getLogger(__name__)

router = APIRouter()


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

    full_text = "\n\n".join(chunk_texts)
    logger.info(
        "Running extraction: document_id=%s chunks=%d", document_id, len(chunk_texts)
    )

    try:
        metrics = await run_extraction(full_text)
    except RuntimeError as exc:
        logger.error("Extraction failed for document_id=%s: %s", document_id, exc)
        raise HTTPException(status_code=500, detail="Metric extraction failed. Please try again.") from exc

    return ExtractionResponse(
        document_id=document_id,
        filename=doc_meta["filename"],
        metrics=metrics,
    )
