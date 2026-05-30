import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.analyst_agent import run_analyst, stream_analyst
from app.agents.conversation_store import (
    get_history,
    new_conversation_id,
    save_history,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalystRequest(BaseModel):
    question: str
    document_ids: list[str] = []
    conversation_id: str | None = None


class AnalystResponse(BaseModel):
    answer: str
    tools_used: list[str]
    conversation_id: str


@router.post("/", response_model=AnalystResponse)
async def analyst(request: AnalystRequest) -> AnalystResponse:
    """Answer a question with the autonomous analyst agent.

    The agent decides which tools to call (document search and/or live market
    data) and returns the synthesized answer plus the tools it used. Pass back
    the returned ``conversation_id`` on the next request to give the agent
    memory of earlier turns.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    conversation_id = request.conversation_id or new_conversation_id()
    history = await get_history(conversation_id)

    try:
        result = await run_analyst(
            request.question, request.document_ids, message_history=history
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Analyst agent failed")
        raise HTTPException(status_code=500, detail="Analyst agent failed.") from exc

    await save_history(conversation_id, result["messages"])

    return AnalystResponse(
        answer=result["answer"],
        tools_used=result["tools_used"],
        conversation_id=conversation_id,
    )


@router.post("/stream")
async def analyst_stream(request: AnalystRequest) -> StreamingResponse:
    """Stream the analyst agent's answer as Server-Sent Events.

    Emits ``event: delta`` frames with incremental answer text, then a final
    ``event: done`` frame carrying ``tools_used`` and the ``conversation_id``.
    The conversation history is persisted server-side after streaming completes.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    conversation_id = request.conversation_id or new_conversation_id()
    history = await get_history(conversation_id)

    async def event_generator():
        try:
            async for event in stream_analyst(
                request.question, request.document_ids, message_history=history
            ):
                if event["type"] == "delta":
                    payload = json.dumps({"text": event["text"]})
                    yield f"event: delta\ndata: {payload}\n\n"
                elif event["type"] == "done":
                    await save_history(conversation_id, event["messages"])
                    payload = json.dumps(
                        {
                            "tools_used": event["tools_used"],
                            "conversation_id": conversation_id,
                        }
                    )
                    yield f"event: done\ndata: {payload}\n\n"
        except Exception:  # noqa: BLE001
            logger.exception("Analyst stream failed")
            payload = json.dumps({"message": "Analyst agent failed."})
            yield f"event: error\ndata: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

