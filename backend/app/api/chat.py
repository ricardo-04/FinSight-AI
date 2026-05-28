import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.research_agent import Citation, ResearchResult, run_research
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    document_ids: list[str] = []


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Answer a financial question using RAG over ingested documents.

    Args:
        request: Contains the user question and optional list of document IDs
            to restrict retrieval to. Omit document_ids to search all documents.

    Returns:
        ChatResponse with the answer and source citations.

    Raises:
        400: If the question is empty.
        500: If the LLM fails after retries.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    logger.info(
        "Chat request: question_length=%d document_ids=%s",
        len(request.question),
        request.document_ids,
    )

    async with AsyncSessionLocal() as session:
        try:
            result: ResearchResult = await run_research(
                question=request.question,
                document_ids=request.document_ids,
                session=session,
            )
        except RuntimeError as exc:
            logger.error("Chat failed: %s", exc)
            raise HTTPException(
                status_code=500,
                detail="Failed to generate an answer. Please try again.",
            ) from exc

    return ChatResponse(answer=result.answer, citations=result.citations)

