"""
Document management service.

Orchestrates the full ingest flow:
  1. Persist a Document record.
  2. Parse the PDF bytes.
  3. Chunk the extracted text.
  4. Ingest chunks into pgvector via the RAG pipeline.

All database interactions use the async SQLAlchemy session passed by the
caller so transactions remain under the caller's control.
"""
import logging
import uuid
from typing import TYPE_CHECKING

from app.models.document import Document
from app.parsing.chunker import chunk_text
from app.parsing.pdf_parser import parse_pdf
from app.rag.pipeline import ingest_document

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def save_document(
    filename: str,
    content: bytes,
    session: "AsyncSession",
) -> str:
    """Parse, embed, and persist a PDF document.

    Args:
        filename: Original filename of the uploaded PDF.
        content: Raw PDF bytes.
        session: An active async SQLAlchemy session. The caller commits.

    Returns:
        The UUID string assigned to the new Document record.

    Raises:
        ValueError: If the PDF cannot be parsed or contains no text.
    """
    document_id = str(uuid.uuid4())
    logger.info(
        "Saving document: filename=%s document_id=%s", filename, document_id
    )

    # Persist the Document metadata row first so foreign keys in
    # document_chunks are satisfied during the flush inside ingest_document.
    doc_row = Document(id=document_id, filename=filename)
    session.add(doc_row)
    await session.flush()

    parsed = parse_pdf(content)
    chunks = chunk_text(parsed.full_text)

    chunk_count = await ingest_document(
        document_id=document_id,
        chunks=chunks,
        session=session,
    )

    logger.info(
        "Document saved: document_id=%s filename=%s chunks=%d",
        document_id,
        filename,
        chunk_count,
    )
    return document_id


async def get_document(
    document_id: str,
    session: "AsyncSession",
) -> dict:
    """Fetch document metadata by ID.

    Args:
        document_id: UUID string of the document.
        session: An active async SQLAlchemy session.

    Returns:
        Dict with keys ``id``, ``filename``, ``created_at``.

    Raises:
        ValueError: If the document does not exist.
    """
    from sqlalchemy import select

    stmt = select(Document).where(Document.id == document_id)
    result = await session.execute(stmt)
    doc = result.scalar_one_or_none()

    if doc is None:
        raise ValueError(f"Document '{document_id}' not found.")

    return {
        "id": doc.id,
        "filename": doc.filename,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }
