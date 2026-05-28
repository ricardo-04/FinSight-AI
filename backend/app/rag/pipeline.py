"""
End-to-end RAG pipeline: embed document chunks and store in pgvector.
"""

async def ingest_document(document_id: str, chunks: list[str]) -> None:
    # TODO: embed chunks and upsert into vector store
    raise NotImplementedError
