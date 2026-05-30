"""
End-to-end RAG ingest pipeline.

Flow: text chunks -> embed_chunks() -> persist DocumentChunk rows with vectors.

Each chunk gets an OpenTelemetry span so ingest latency is traceable per
document in the collector dashboard.
"""
import logging
import uuid
from typing import TYPE_CHECKING

from opentelemetry import trace

from app.db.session import DATABASE_URL
from app.models.document import DocumentChunk
from app.rag.embeddings import embed_chunks

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_USE_PGVECTOR: bool = not DATABASE_URL.startswith("sqlite")


async def ingest_document(
    document_id: str,
    chunks: list[str],
    session: "AsyncSession",
) -> int:
    """Embed *chunks* and persist them as DocumentChunk rows for *document_id*.

    Args:
        document_id: The UUID string of the parent Document record.
        chunks: List of text strings produced by the chunker.
        session: An active async SQLAlchemy session. The caller is responsible
            for committing or rolling back.

    Returns:
        The number of chunks stored.

    Raises:
        ValueError: If *chunks* is empty.
    """
    if not chunks:
        raise ValueError("Cannot ingest an empty chunk list.")

    with tracer.start_as_current_span("rag.ingest_document") as span:
        span.set_attribute("document_id", document_id)
        span.set_attribute("chunk_count", len(chunks))

        logger.info(
            "Ingesting document: document_id=%s chunks=%d",
            document_id,
            len(chunks),
        )

        if _USE_PGVECTOR:
            embeddings = await embed_chunks(chunks)
        else:
            # SQLite dev mode: skip embedding generation
            embeddings = [None] * len(chunks)

        chunk_rows = [
            DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=document_id,
                chunk_index=idx,
                text=text,
                embedding=vector,
            )
            for idx, (text, vector) in enumerate(zip(chunks, embeddings))
        ]

        session.add_all(chunk_rows)
        # Flush so the rows are visible within this transaction if needed;
        # the caller commits.
        await session.flush()

        logger.info(
            "Ingested %d chunks for document_id=%s", len(chunk_rows), document_id
        )
        return len(chunk_rows)
