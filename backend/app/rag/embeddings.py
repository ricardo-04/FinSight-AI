"""
Embedding generation via the active LLM provider.

All calls go through get_raw_client() and get_embedding_config() from
llm_provider so that the provider (NIM, Ollama, OpenAI) is swapped by env var
without changing this module.

NVIDIA NIM note: the nv-embedqa-e5-v5 model requires an ``input_type``
field in extra_body. Other providers ignore unknown extra_body fields.
"""
import logging
import os
from typing import Literal

from app.services.llm_provider import get_embedding_config, get_raw_client

logger = logging.getLogger(__name__)

# For NIM: "query" when embedding a search query; "passage" when embedding
# document chunks. Set via EMBEDDING_INPUT_TYPE env var (default "passage").
_INPUT_TYPE: Literal["query", "passage"] = os.getenv(  # type: ignore[assignment]
    "EMBEDDING_INPUT_TYPE", "passage"
)


async def embed_text(text: str, input_type: str = _INPUT_TYPE) -> list[float]:
    """Generate a single embedding vector for *text*.

    Args:
        text: The text to embed. Will be truncated to avoid exceeding the
            model's token limit.
        input_type: ``"passage"`` for document chunks (default),
            ``"query"`` for search queries. Only meaningful for NIM models.

    Returns:
        A list of floats representing the embedding vector.
    """
    config = get_embedding_config()
    client = get_raw_client()

    truncated = text[:8000]  # Conservative limit; NIM max is ~8192 tokens
    extra_body: dict = {"input_type": input_type, "truncate": "END"}

    response = await client.embeddings.create(
        input=[truncated],
        model=config["model"],
        extra_body=extra_body,
    )
    return response.data[0].embedding


async def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Generate embedding vectors for a list of text chunks.

    Processes chunks sequentially to avoid rate-limit bursts. For large
    document sets, consider batching with a semaphore.

    Args:
        chunks: List of text strings to embed.

    Returns:
        List of embedding vectors in the same order as *chunks*.
    """
    if not chunks:
        return []

    config = get_embedding_config()
    client = get_raw_client()

    truncated_chunks = [c[:8000] for c in chunks]
    extra_body: dict = {"input_type": "passage", "truncate": "END"}

    logger.debug(
        "Embedding %d chunks with model=%s", len(chunks), config["model"]
    )

    response = await client.embeddings.create(
        input=truncated_chunks,
        model=config["model"],
        extra_body=extra_body,
    )

    # The API guarantees ordering by index, but sort defensively
    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]


async def embed_query(query: str) -> list[float]:
    """Generate an embedding vector for a search query.

    Uses ``input_type="query"`` so NIM models apply the query-optimized
    transformation. Use this when embedding user questions for retrieval;
    use :func:`embed_chunks` when embedding document text.

    Args:
        query: The search query text.

    Returns:
        A list of floats representing the query embedding vector.
    """
    return await embed_text(query, input_type="query")
