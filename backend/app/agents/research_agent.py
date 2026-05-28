"""
Research Agent - answers user questions using RAG retrieval over ingested documents.

Flow:
  1. Retrieve the top-K most relevant chunks via rag/retrieval.py.
  2. Assemble a context block from those chunks with source references.
  3. Call the LLM via PydanticAI to produce a grounded answer.
  4. Return the answer with citations so the frontend can link back to sources.

All LLM calls go through llm_provider. Provider is selected via LLM_PROVIDER env var.
"""
import logging
import os
from typing import TYPE_CHECKING

from opentelemetry import trace
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelRetry, UnexpectedModelBehavior

from app.rag.retrieval import retrieve
from app.services.llm_provider import get_chat_model

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_MAX_RETRIES: int = int(os.getenv("RESEARCH_MAX_RETRIES", "2"))
_MAX_INPUT_LENGTH: int = int(os.getenv("MAX_PROMPT_INPUT_LENGTH", "8000"))

_SYSTEM_PROMPT = """\
You are a financial research assistant. You answer questions about companies,
earnings reports, SEC filings, and investor presentations based ONLY on the
context provided below.

Rules:
- Answer using only the provided context. Do not use external knowledge.
- If the context does not contain enough information to answer, say so clearly.
- Keep your answer concise and factual.
- Do not fabricate figures, dates, or company names.
- Reference the source number (e.g. [1], [2]) when using information from a specific chunk.
"""


class Citation(BaseModel):
    """A reference to a source chunk used in the answer."""

    document_id: str = Field(description="UUID of the source document")
    chunk_index: int = Field(description="Index of the chunk within the document")
    snippet: str = Field(description="Short excerpt from the source chunk")


class ResearchResult(BaseModel):
    """Structured output of the research agent."""

    answer: str = Field(default="", description="The answer to the user's question")
    citations: list[Citation] = Field(
        default_factory=list, description="Sources used in the answer"
    )


_agent: Agent[None, ResearchResult] | None = None


def _get_agent() -> "Agent[None, ResearchResult]":
    """Lazily initialise the PydanticAI agent."""
    global _agent
    if _agent is None:
        _agent = Agent(
            model=get_chat_model(),
            output_type=ResearchResult,
            system_prompt=_SYSTEM_PROMPT,
            retries=_MAX_RETRIES,
        )
    return _agent


def _build_context_block(hits: list[dict]) -> str:
    """Format retrieval results into a numbered context block for the LLM."""
    lines: list[str] = []
    for i, hit in enumerate(hits, start=1):
        lines.append(
            f"[{i}] (document={hit['document_id']}, chunk={hit['chunk_index']}, "
            f"score={hit['score']:.3f})\n{hit['text']}"
        )
    return "\n\n".join(lines)


async def run_research(
    question: str,
    document_ids: list[str],
    session: "AsyncSession",
) -> ResearchResult:
    """Answer *question* using RAG retrieval over *document_ids*.

    Args:
        question: The user's question. Will be sanitized and truncated.
        document_ids: List of document UUIDs to restrict retrieval to.
            Pass an empty list to search all ingested documents.
        session: An active async SQLAlchemy session for retrieval queries.

    Returns:
        A ResearchResult with the answer and citations.

    Raises:
        RuntimeError: If the LLM fails after all retries.
    """
    sanitized_question = question.strip().replace("\x00", "")[:_MAX_INPUT_LENGTH]
    if not sanitized_question:
        return ResearchResult(answer="Please provide a question.")

    with tracer.start_as_current_span("agent.research") as span:
        span.set_attribute("question_length", len(sanitized_question))
        span.set_attribute("document_ids", ",".join(document_ids))

        hits = await retrieve(
            query=sanitized_question,
            session=session,
            document_ids=document_ids or None,
        )

        if not hits:
            logger.info("No relevant chunks found for question: %s", sanitized_question[:80])
            return ResearchResult(
                answer="I could not find relevant information in the uploaded documents to answer this question."
            )

        context_block = _build_context_block(hits)
        user_prompt = (
            f"Context:\n{context_block}\n\n"
            f"Question: {sanitized_question}"
        )

        span.set_attribute("context_chunks", len(hits))

        try:
            result = await _get_agent().run(user_prompt)
            research = result.output
            logger.info(
                "Research complete: answer_length=%d citations=%d",
                len(research.answer),
                len(research.citations),
            )
            return research

        except (ModelRetry, UnexpectedModelBehavior) as exc:
            logger.error("Research agent failed: %s", exc)
            raise RuntimeError("LLM failed to produce a valid research response.") from exc

