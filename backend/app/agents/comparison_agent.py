"""
Comparison Agent — compares financial metrics across two or more documents.

Flow:
  1. Run the extraction agent on each document's text.
  2. Build a structured side-by-side comparison table.
  3. Pass it to an LLM to produce a human-readable analysis with delta values.

All LLM calls go through llm_provider.
"""
import logging
import os
from typing import TYPE_CHECKING

from opentelemetry import trace
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelRetry, UnexpectedModelBehavior
from sqlalchemy import select

from app.agents.extraction_agent import FinancialMetrics, run_extraction
from app.models.document import DocumentChunk
from app.services.llm_provider import get_chat_model

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_MAX_RETRIES: int = int(os.getenv("COMPARISON_MAX_RETRIES", "2"))
_MAX_CHUNK_CHARS: int = int(os.getenv("MAX_PROMPT_INPUT_LENGTH", "8000"))

_SYSTEM_PROMPT = """\
You are a financial analyst assistant. You will receive a structured comparison
table of financial metrics for two or more companies or reporting periods.

Your task:
- Summarise the key differences between the entries.
- Highlight delta values where possible (e.g. revenue difference, growth gap).
- Note which company / period appears stronger and why.
- Keep the analysis concise (3-5 paragraphs).
- Use only the data provided. Do not infer or fabricate numbers.
"""


class DocumentMetrics(BaseModel):
    """Metrics extracted from a single document."""

    document_id: str = Field(description="UUID of the source document")
    filename: str = Field(default="", description="Original filename")
    metrics: FinancialMetrics = Field(description="Extracted financial metrics")


class ComparisonResult(BaseModel):
    """Structured comparison output returned by the agent."""

    documents: list[DocumentMetrics] = Field(
        description="Metrics for each compared document"
    )
    analysis: str = Field(
        description="Human-readable comparative analysis with delta values"
    )


_agent: Agent[None, ComparisonResult] | None = None


def _get_agent() -> "Agent[None, ComparisonResult]":
    global _agent
    if _agent is None:
        _agent = Agent(
            model=get_chat_model(),
            output_type=ComparisonResult,
            system_prompt=_SYSTEM_PROMPT,
            retries=_MAX_RETRIES,
        )
    return _agent


async def _load_text(document_id: str, session: "AsyncSession") -> str:
    """Fetch and concatenate all chunks for *document_id* ordered by index."""
    result = await session.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )
    chunks = result.scalars().all()
    return "\n\n".join(c.text for c in chunks)[:_MAX_CHUNK_CHARS]


async def run_comparison(
    document_ids: list[str],
    session: "AsyncSession",
) -> ComparisonResult:
    """Compare financial metrics across *document_ids*.

    Args:
        document_ids: List of 2+ document UUIDs to compare.
        session:      Active SQLAlchemy async session.

    Returns:
        ComparisonResult with per-document metrics and a comparative analysis.

    Raises:
        ValueError: If fewer than 2 document IDs are provided.
        RuntimeError: If the LLM returns an unexpected response.
    """
    if len(document_ids) < 2:
        raise ValueError("At least 2 document IDs are required for comparison.")

    with tracer.start_as_current_span("agent.comparison") as span:
        span.set_attribute("document_count", len(document_ids))

        # Step 1: extract metrics per document
        doc_metrics: list[DocumentMetrics] = []
        for doc_id in document_ids:
            text = await _load_text(doc_id, session)
            if not text.strip():
                logger.warning("No chunks found for document %s — skipping", doc_id)
                doc_metrics.append(
                    DocumentMetrics(document_id=doc_id, metrics=FinancialMetrics())
                )
                continue
            metrics = await run_extraction(text)
            doc_metrics.append(DocumentMetrics(document_id=doc_id, metrics=metrics))

        # Step 2: build structured prompt for the comparison LLM call
        rows = []
        for dm in doc_metrics:
            m = dm.metrics
            rows.append(
                f"Document: {dm.document_id}\n"
                f"  Company : {m.company or 'N/A'}\n"
                f"  Quarter : {m.quarter or 'N/A'}\n"
                f"  Revenue : {m.revenue or 'N/A'}\n"
                f"  Growth  : {m.growth or 'N/A'}\n"
                f"  Guidance: {m.guidance or 'N/A'}\n"
                f"  Risks   : {'; '.join(m.risks) if m.risks else 'N/A'}"
            )
        comparison_table = "\n\n".join(rows)

        prompt = (
            "Compare the following financial metrics and provide a structured analysis:\n\n"
            f"{comparison_table}"
        )

        # Step 3: call the LLM for analysis
        try:
            agent = _get_agent()
            result = await agent.run(prompt)
            output = result.output
        except (ModelRetry, UnexpectedModelBehavior) as exc:
            logger.error("Comparison agent failed: %s", exc)
            raise RuntimeError(f"Comparison agent error: {exc}") from exc

        # Attach the per-document metrics we already extracted
        output.documents = doc_metrics
        span.set_attribute("analysis_length", len(output.analysis))
        return output

