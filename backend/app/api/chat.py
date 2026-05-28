from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    document_ids: list[str] = []

@router.post("/")
async def chat(request: ChatRequest):
    # TODO: run research agent with RAG retrieval
    return {"answer": "", "citations": []}
