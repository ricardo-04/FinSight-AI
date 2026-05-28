"""Document management service."""

async def save_document(filename: str, content: bytes) -> str:
    raise NotImplementedError

async def get_document(document_id: str) -> dict:
    raise NotImplementedError
