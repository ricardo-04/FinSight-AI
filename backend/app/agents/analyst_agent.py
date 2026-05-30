"""
Autonomous analyst agent.

Unlike the other agents (which are single-shot LLM calls with a fixed context),
this agent is *truly agentic*: it is given tools via PydanticAI's ``@agent.tool``
decorator and decides on its own which tools to call, in what order, and how to
combine their results to answer the user's question.

Tools exposed to the model:
  - search_documents      -> semantic/hybrid RAG over uploaded documents
  - get_company_financials -> live market data from FMP

The model performs multi-step reasoning: it may call search_documents, inspect
the result, then call get_company_financials, and finally synthesize an answer.
All numbers come from tool output; the model is instructed never to invent them.
"""
import asyncio
import logging
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from opentelemetry import trace
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import UsageLimits

from app.prompts import ANALYST_AGENT_SYSTEM, get_prompt
from app.services.llm_provider import get_chat_model

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_MAX_RETRIES: int = int(os.getenv("ANALYST_AGENT_MAX_RETRIES", "2"))
_TOOL_TOP_K: int = int(os.getenv("ANALYST_AGENT_TOP_K", "6"))
# Guardrails: bound how hard the agent can work on a single question so a runaway
# tool loop can never blow up cost or latency.
_REQUEST_LIMIT: int = int(os.getenv("ANALYST_AGENT_REQUEST_LIMIT", "6"))
_TOOL_CALLS_LIMIT: int = int(os.getenv("ANALYST_AGENT_TOOL_CALLS_LIMIT", "8"))
# Per-tool wall-clock timeout (seconds) so one slow dependency cannot hang a run.
_TOOL_TIMEOUT: float = float(os.getenv("ANALYST_AGENT_TOOL_TIMEOUT", "20"))
# Cap tool output fed back into the model context to bound token usage.
_MAX_TOOL_CHARS: int = int(os.getenv("ANALYST_AGENT_MAX_TOOL_CHARS", "6000"))

_SYSTEM_PROMPT = get_prompt("analyst_agent", ANALYST_AGENT_SYSTEM)

_USAGE_LIMITS = UsageLimits(
    request_limit=_REQUEST_LIMIT,
    tool_calls_limit=_TOOL_CALLS_LIMIT,
)


def _truncate(text: str) -> str:
    """Bound tool output so a single tool cannot flood the model context."""
    if len(text) <= _MAX_TOOL_CHARS:
        return text
    return text[:_MAX_TOOL_CHARS] + "\n\n[...output truncated to fit context budget...]"


@dataclass
class AnalystDeps:
    """Per-run dependencies passed to tool calls.

    ``document_ids`` scopes document search to the user's selection. ``tools_used``
    records which tools the model invoked so callers can surface the agent's path.
    """

    document_ids: list[str] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)


_agent: "Agent[AnalystDeps, str] | None" = None


def _get_agent() -> "Agent[AnalystDeps, str]":
    """Lazily build the agent and register its tools."""
    global _agent
    if _agent is not None:
        return _agent

    agent = Agent(
        model=get_chat_model(),
        deps_type=AnalystDeps,
        output_type=str,
        system_prompt=_SYSTEM_PROMPT,
        retries=_MAX_RETRIES,
        # The NVIDIA llama-3.3 endpoint supports only one tool call per step.
        # Force sequential tool calls so the agent never emits a parallel batch
        # the model would reject with a 500.
        model_settings={"parallel_tool_calls": False},
    )

    @agent.tool
    async def search_documents(ctx: RunContext[AnalystDeps], query: str) -> str:
        """Search the user's uploaded financial documents for relevant passages.

        Args:
            query: A focused natural-language search query.
        """
        from app.tools.vector_search import vector_search

        ctx.deps.tools_used.append("search_documents")
        with tracer.start_as_current_span("tool.search_documents") as span:
            span.set_attribute("query_length", len(query))
            span.set_attribute("top_k", _TOOL_TOP_K)
            try:
                hits = await asyncio.wait_for(
                    vector_search(
                        query=query,
                        top_k=_TOOL_TOP_K,
                        document_ids=ctx.deps.document_ids or None,
                    ),
                    timeout=_TOOL_TIMEOUT,
                )
            except asyncio.TimeoutError:
                span.set_attribute("timed_out", True)
                logger.warning("search_documents timed out after %ss", _TOOL_TIMEOUT)
                return "Document search timed out. Please try a narrower query."
            span.set_attribute("hit_count", len(hits))
            if not hits:
                return "No relevant passages found in the uploaded documents."
            output = "\n\n".join(
                f"[doc={h['document_id']} chunk={h['chunk_index']} "
                f"score={h['score']:.3f}]\n{h['text']}"
                for h in hits
            )
            return _truncate(output)

    @agent.tool
    async def get_company_financials(ctx: RunContext[AnalystDeps], ticker: str) -> str:
        """Get live financial data (profile, income statement, key ratios) for a ticker.

        Args:
            ticker: Stock ticker symbol, e.g. "AAPL", "MSFT", "NVDA".
        """
        from app.services.fmp_service import (
            get_company_profile,
            get_income_statement,
            get_key_ratios,
        )

        ctx.deps.tools_used.append("get_company_financials")
        with tracer.start_as_current_span("tool.get_company_financials") as span:
            span.set_attribute("ticker", ticker)
            try:
                profile = await asyncio.wait_for(
                    get_company_profile(ticker), timeout=_TOOL_TIMEOUT
                )
                income = await asyncio.wait_for(
                    get_income_statement(ticker, limit=1), timeout=_TOOL_TIMEOUT
                )
                ratios = await asyncio.wait_for(
                    get_key_ratios(ticker, limit=1), timeout=_TOOL_TIMEOUT
                )
            except asyncio.TimeoutError:
                span.set_attribute("timed_out", True)
                logger.warning("get_company_financials timed out for %s", ticker)
                return f"Live financial data lookup for '{ticker}' timed out."
            span.set_attribute("found", bool(profile))
            if not profile:
                return f"No financial data found for ticker '{ticker}'."
            output = (
                f"Profile: {profile}\n\n"
                f"Latest income statement: {income[0] if income else 'N/A'}\n\n"
                f"Key ratios: {ratios[0] if ratios else 'N/A'}"
            )
            return _truncate(output)

    _agent = agent
    return _agent


async def run_analyst(
    question: str,
    document_ids: list[str] | None = None,
    message_history: list[ModelMessage] | None = None,
) -> dict:
    """Answer *question* by letting the agent autonomously call its tools.

    Args:
        question: The user's natural-language question.
        document_ids: Optional document scope for the search tool.
        message_history: Prior conversation messages so the agent has memory of
            earlier turns. Pass the ``messages`` returned from a previous call.

    Returns:
        Dict with ``answer`` (str), ``tools_used`` (list[str]) and ``messages``
        (the full updated message history to feed into the next turn).
    """
    deps = AnalystDeps(document_ids=document_ids or [])
    with tracer.start_as_current_span("agent.analyst") as span:
        span.set_attribute("question_length", len(question))
        span.set_attribute("has_history", bool(message_history))
        agent = _get_agent()
        result = await agent.run(
            question,
            deps=deps,
            message_history=message_history,
            usage_limits=_USAGE_LIMITS,
        )
        span.set_attribute("tools_used", ",".join(deps.tools_used))

    return {
        "answer": result.output,
        "tools_used": deps.tools_used,
        "messages": result.all_messages(),
    }


async def stream_analyst(
    question: str,
    document_ids: list[str] | None = None,
    message_history: list[ModelMessage] | None = None,
) -> AsyncIterator[dict]:
    """Stream the analyst agent's answer incrementally.

    Yields dicts describing stream events:
        - ``{"type": "delta", "text": str}`` for each new chunk of answer text.
        - ``{"type": "done", "tools_used": list[str], "messages": list}`` once,
          at the end, carrying the tools the agent used and the updated history.

    The model decides which tools to call before producing text; tool calls are
    not streamed token-by-token, only the final synthesized answer is.
    """
    deps = AnalystDeps(document_ids=document_ids or [])
    with tracer.start_as_current_span("agent.analyst.stream") as span:
        span.set_attribute("question_length", len(question))
        span.set_attribute("has_history", bool(message_history))
        agent = _get_agent()
        async with agent.run_stream(
            question,
            deps=deps,
            message_history=message_history,
            usage_limits=_USAGE_LIMITS,
        ) as result:
            async for delta in result.stream_text(delta=True):
                yield {"type": "delta", "text": delta}
            span.set_attribute("tools_used", ",".join(deps.tools_used))
            yield {
                "type": "done",
                "tools_used": deps.tools_used,
                "messages": result.all_messages(),
            }
