"""
Semantic search over pgvector embeddings.
"""

async def retrieve(query: str, top_k: int = 5) -> list[dict]:
    # TODO: embed query, run pgvector similarity search
    raise NotImplementedError
