from fastapi import APIRouter

router = APIRouter()

@router.post("/{document_id}")
async def extract_metrics(document_id: str):
    # TODO: run extraction agent on document chunks
    return {"document_id": document_id, "status": "queued"}
