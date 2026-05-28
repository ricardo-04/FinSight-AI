"""Vector search tool for agent use.

Wraps the RAG retrieval layer so agents can invoke semantic search
as a tool call during multi-step reasoning.
"""

from app.db.session import AsyncSessionLocal
from app.rag.retrieval import retrieve


async def vector_search(query: str, top_k: int = 5, document_ids: list[str] | None = None) -> list[dict]:
    """Search ingested documents for chunks semantically similar to *query*.

    Args:
        query: Natural language search query.
        top_k: Maximum number of results to return (default 5).
        document_ids: Optional list of document UUIDs to restrict the search.

    Returns:
        List of dicts with keys: document_id, chunk_index, text, score.
        Ordered by descending similarity score.
    """
    async with AsyncSessionLocal() as session:
        results = await retrieve(
            query=query,
            session=session,
            document_ids=document_ids,
            top_k=top_k,
        )
    return results
