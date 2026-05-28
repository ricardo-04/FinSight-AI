"""
Split extracted text into overlapping word-based chunks for embedding.

Chunk size and overlap are read from environment variables so they can
be tuned without code changes:
  CHUNK_SIZE    - number of words per chunk (default 512)
  CHUNK_OVERLAP - number of words to repeat between consecutive chunks (default 64)
"""
import logging
import os

logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
_DEFAULT_CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "64"))


def chunk_text(
    text: str,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
    overlap: int = _DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split *text* into overlapping word-based chunks.

    Args:
        text: The input text to split.
        chunk_size: Number of words per chunk.
        overlap: Number of words shared between consecutive chunks.

    Returns:
        List of text chunks. Empty list if *text* is blank.

    Raises:
        ValueError: If chunk_size <= 0 or overlap >= chunk_size.
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be less than chunk_size ({chunk_size})"
        )

    text = text.strip()
    if not text:
        return []

    words = text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks: list[str] = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += step

    logger.debug(
        "Chunked text: words=%d chunk_size=%d overlap=%d -> %d chunks",
        len(words),
        chunk_size,
        overlap,
        len(chunks),
    )
    return chunks
