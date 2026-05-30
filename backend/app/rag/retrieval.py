"""
Semantic retrieval over document embeddings.

When running with PostgreSQL+pgvector, uses native cosine distance operator.
When running with SQLite (dev mode), falls back to returning all chunks
for the requested documents (no vector filtering) — the LLM still gets
relevant context since chunks are small and scoped to selected documents.
"""
import logging
import os
import re
from typing import TYPE_CHECKING

from opentelemetry import trace
from sqlalchemy import select, text

from app.db.session import DATABASE_URL
from app.models.document import DocumentChunk
from app.rag.embeddings import embed_query

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_DEFAULT_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
_SCORE_THRESHOLD: float = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.75"))
_USE_PGVECTOR: bool = not DATABASE_URL.startswith("sqlite")

# Hybrid reranking weights. The vector (semantic) score dominates, while the
# lexical keyword score breaks ties and rescues exact-term matches that the
# embedding model ranks slightly lower (e.g. tickers, line-item names).
_VECTOR_WEIGHT: float = float(os.getenv("RAG_VECTOR_WEIGHT", "0.7"))
_KEYWORD_WEIGHT: float = float(os.getenv("RAG_KEYWORD_WEIGHT", "0.3"))

_TOKEN_RE = re.compile(r"[a-z0-9]+")


# --------------------------------------------------------------------------- #
# Hybrid reranking helpers (pure, deterministic — exercised directly by evals) #
# --------------------------------------------------------------------------- #
def _tokenize(value: str) -> list[str]:
    """Lowercase *value* and split it into alphanumeric word tokens."""
    return _TOKEN_RE.findall(value.lower())


def _keyword_score(query_terms: list[str], chunk_text: str) -> float:
    """Fraction of the unique query terms that appear in *chunk_text* (0-1)."""
    unique_terms = set(query_terms)
    if not unique_terms:
        return 0.0
    chunk_tokens = set(_tokenize(chunk_text))
    matched = sum(1 for term in unique_terms if term in chunk_tokens)
    return matched / len(unique_terms)


def _fuse(vector_score: float, keyword_score: float) -> float:
    """Combine a semantic *vector_score* and a lexical *keyword_score*."""
    return _VECTOR_WEIGHT * vector_score + _KEYWORD_WEIGHT * keyword_score


def _rerank_hybrid(query: str, hits: list[dict]) -> list[dict]:
    """Reorder *hits* by fused semantic + lexical score.

    The original ``score`` (vector similarity) is preserved on each hit; only
    the ordering changes, so downstream consumers and citations are unaffected.
    """
    if not hits:
        return hits
    query_terms = _tokenize(query)
    ranked = sorted(
        hits,
        key=lambda hit: _fuse(
            float(hit["score"]),
            _keyword_score(query_terms, hit["text"]),
        ),
        reverse=True,
    )
    return ranked


async def retrieve(
    query: str,
    session: "AsyncSession",
    document_ids: list[str] | None = None,
    top_k: int = _DEFAULT_TOP_K,
    score_threshold: float = _SCORE_THRESHOLD,
) -> list[dict]:
    """Retrieve the most semantically similar chunks for *query*.

    Args:
        query: The user's search question or text.
        session: An active async SQLAlchemy session.
        document_ids: Optional list of document UUIDs to restrict the search.
            If None, searches across all ingested documents.
        top_k: Maximum number of results to return.
        score_threshold: Minimum cosine similarity score (0-1). Results below
            this threshold are discarded.

    Returns:
        List of dicts, each containing:
            - ``document_id`` (str)
            - ``chunk_index`` (int)
            - ``text`` (str)
            - ``score`` (float) - cosine similarity, higher is better
        Ordered by descending score. Empty list if no results meet the threshold.
    """
    with tracer.start_as_current_span("rag.retrieve") as span:
        span.set_attribute("top_k", top_k)
        span.set_attribute("score_threshold", score_threshold)

        if _USE_PGVECTOR:
            hits = await _retrieve_pgvector(query, session, document_ids, top_k, score_threshold, span)
        else:
            hits = await _retrieve_sqlite(query, session, document_ids, top_k, span)

        return _rerank_hybrid(query, hits)


async def _retrieve_pgvector(query, session, document_ids, top_k, score_threshold, span):
    query_vector = await embed_query(query)

    distance_expr = text(
        "1 - (embedding <=> CAST(:qv AS vector)) AS score"
    )

    stmt = (
        select(
            DocumentChunk.document_id,
            DocumentChunk.chunk_index,
            DocumentChunk.text,
            distance_expr,
        )
        .where(
            text("1 - (embedding <=> CAST(:qv AS vector)) >= :threshold")
        )
        .order_by(text("score DESC"))
        .limit(top_k)
    )
    params: dict = {
        "qv": str(query_vector),
        "threshold": score_threshold,
    }

    if document_ids:
        stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))
        span.set_attribute("document_ids", ",".join(document_ids))

    result = await session.execute(stmt, params)
    rows = result.fetchall()

    hits = [
        {
            "document_id": row.document_id,
            "chunk_index": row.chunk_index,
            "text": row.text,
            "score": float(row.score),
        }
        for row in rows
    ]

    logger.info(
        "Retrieval (pgvector): query_len=%d results=%d top_score=%s",
        len(query),
        len(hits),
        f"{hits[0]['score']:.4f}" if hits else "n/a",
    )
    return hits


async def _retrieve_sqlite(query, session, document_ids, top_k, span):
    """Fallback retrieval for SQLite dev mode.

    Returns the first top_k chunks matching the document filter,
    ordered by chunk_index. Assigns a synthetic score of 0.85.
    """
    stmt = (
        select(
            DocumentChunk.document_id,
            DocumentChunk.chunk_index,
            DocumentChunk.text,
        )
        .order_by(DocumentChunk.chunk_index)
        .limit(top_k)
    )

    if document_ids:
        stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))
        span.set_attribute("document_ids", ",".join(document_ids))

    result = await session.execute(stmt)
    rows = result.fetchall()

    hits = [
        {
            "document_id": row.document_id,
            "chunk_index": row.chunk_index,
            "text": row.text,
            "score": 0.85,
        }
        for row in rows
    ]

    logger.info(
        "Retrieval (sqlite fallback): query_len=%d results=%d",
        len(query),
        len(hits),
    )
    return hits
