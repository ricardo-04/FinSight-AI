"""
Extraction Agent - pulls structured financial metrics from document text using a LLM.

Uses PydanticAI with a structured output model so the LLM response is
automatically validated. If the model returns a partial or malformed response,
the agent retries up to MAX_RETRIES times before returning a best-effort
result with empty fields.

All calls go through llm_provider so the active provider (NIM / Ollama /
OpenAI) is selected via the LLM_PROVIDER environment variable.
"""
import logging
import os

from opentelemetry import trace
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelRetry, UnexpectedModelBehavior

from app.services.llm_provider import get_chat_model

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_MAX_RETRIES: int = int(os.getenv("EXTRACTION_MAX_RETRIES", "2"))

_SYSTEM_PROMPT = """\
You are a financial data extraction assistant. Your task is to extract
structured financial metrics from earnings reports, SEC filings, and
investor presentations.

Given document text, extract the following fields:
- company: company name (string)
- quarter: reporting period, e.g. "Q1 2026" (string)
- revenue: total revenue figure with currency and units, e.g. "$4.2B" (string)
- growth: year-over-year revenue growth percentage, e.g. "+12% YoY" (string)
- guidance: forward guidance statement for the next quarter or year (string)
- risks: list of key risk factors mentioned (list of strings, max 5)

Rules:
- Use ONLY information present in the provided text. Do not infer or fabricate.
- If a field is not found in the text, use an empty string or empty list.
- Keep each risk item concise - one sentence maximum.
- Do not include markdown formatting in your response.
"""


class FinancialMetrics(BaseModel):
    """Structured financial metrics extracted from a document."""

    company: str = Field(default="", description="Company name")
    quarter: str = Field(default="", description="Reporting period, e.g. Q1 2026")
    revenue: str = Field(default="", description="Total revenue with currency and units")
    growth: str = Field(default="", description="Year-over-year revenue growth percentage")
    guidance: str = Field(default="", description="Forward guidance statement")
    risks: list[str] = Field(default_factory=list, description="Key risk factors (max 5)")


_agent: Agent[None, FinancialMetrics] | None = None


def _get_agent() -> "Agent[None, FinancialMetrics]":
    """Lazily initialise the PydanticAI agent so the LLM provider is resolved
    at runtime (after env vars are loaded) rather than at import time."""
    global _agent
    if _agent is None:
        _agent = Agent(
            model=get_chat_model(),
            output_type=FinancialMetrics,
            system_prompt=_SYSTEM_PROMPT,
            retries=_MAX_RETRIES,
        )
    return _agent


async def run_extraction(text: str, max_length: int | None = None) -> FinancialMetrics:
    """Extract structured financial metrics from *text*.

    Args:
        text: Raw text from a parsed PDF document or a concatenated set of
            chunks. Will be sanitized and truncated before being sent to
            the LLM.
        max_length: Maximum number of characters to send to the LLM. Defaults
            to the EXTRACTION_MAX_INPUT_LENGTH env var (falling back to
            MAX_PROMPT_INPUT_LENGTH) so long filings keep enough room for the
            financial statements after the cover page.

    Returns:
        A FinancialMetrics instance. Fields not found in the text are empty
        strings or empty lists - never raises on partial results.

    Raises:
        RuntimeError: If the LLM fails after all retries and returns an
            unusable response.
    """
    if max_length is None:
        max_length = int(
            os.getenv("EXTRACTION_MAX_INPUT_LENGTH")
            or os.getenv("MAX_PROMPT_INPUT_LENGTH", "8000")
        )
    sanitized = text.strip().replace("\x00", "")[:max_length]

    if not sanitized:
        logger.warning("run_extraction called with empty text; returning empty metrics.")
        return FinancialMetrics()

    with tracer.start_as_current_span("agent.extraction") as span:
        span.set_attribute("input_length", len(sanitized))

        try:
            result = await _get_agent().run(sanitized)
            metrics = result.output
            span.set_attribute("company", metrics.company)
            span.set_attribute("quarter", metrics.quarter)
            logger.info(
                "Extraction complete: company=%s quarter=%s",
                metrics.company,
                metrics.quarter,
            )
            return metrics

        except ModelRetry as exc:
            logger.warning("Extraction agent retry exhausted: %s", exc)
            raise RuntimeError(
                "LLM failed to return valid financial metrics after retries."
            ) from exc

        except UnexpectedModelBehavior as exc:
            logger.error("Unexpected LLM behavior during extraction: %s", exc)
            raise RuntimeError(
                "LLM returned an unexpected response during extraction."
            ) from exc
