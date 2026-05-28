"""
Tests for agents/extraction_agent.py, agents/research_agent.py, and
agents/comparison_agent.py.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.comparison_agent import ComparisonResult, DocumentMetrics, run_comparison
from app.agents.extraction_agent import FinancialMetrics, run_extraction
from app.agents.research_agent import Citation, ResearchResult, run_research


# ---------------------------------------------------------------------------
# extraction_agent
# ---------------------------------------------------------------------------

class TestRunExtraction:
    @pytest.mark.asyncio
    async def test_returns_financial_metrics(self, mock_llm_extraction):
        result = await run_extraction("Acme Corp Q1 2026 revenue $4.2B growth 12%")
        assert isinstance(result, FinancialMetrics)
        assert result.company == "Acme Corp"
        assert result.quarter == "Q1 2026"

    @pytest.mark.asyncio
    async def test_empty_text_returns_empty_metrics(self):
        result = await run_extraction("")
        assert isinstance(result, FinancialMetrics)
        assert result.company == ""

    @pytest.mark.asyncio
    async def test_whitespace_only_returns_empty_metrics(self):
        result = await run_extraction("   ")
        assert result.company == ""

    @pytest.mark.asyncio
    async def test_text_truncated_to_max_length(self, mock_llm_extraction):
        """Input longer than MAX_PROMPT_INPUT_LENGTH should not raise."""
        long_text = "word " * 10000
        result = await run_extraction(long_text)
        assert isinstance(result, FinancialMetrics)

    @pytest.mark.asyncio
    async def test_llm_failure_raises_runtime_error(self):
        from pydantic_ai.exceptions import ModelRetry

        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(side_effect=ModelRetry("failed"))

        with patch("app.agents.extraction_agent._get_agent", return_value=mock_agent):
            with pytest.raises(RuntimeError, match="retries"):
                await run_extraction("some financial text")


# ---------------------------------------------------------------------------
# research_agent
# ---------------------------------------------------------------------------

class TestRunResearch:
    @pytest.mark.asyncio
    async def test_returns_research_result(self, mock_llm_research, db_session):
        with patch("app.agents.research_agent.retrieve", new=AsyncMock(return_value=[
            {"document_id": "doc-123", "chunk_index": 0, "text": "Acme revenue $4.2B", "score": 0.92}
        ])):
            result = await run_research("What was Acme revenue?", ["doc-123"], db_session)

        assert isinstance(result, ResearchResult)
        assert len(result.answer) > 0

    @pytest.mark.asyncio
    async def test_empty_question_returns_prompt(self, db_session):
        result = await run_research("", [], db_session)
        assert "question" in result.answer.lower()

    @pytest.mark.asyncio
    async def test_no_retrieval_hits_returns_no_info_message(self, db_session):
        with patch("app.agents.research_agent.retrieve", new=AsyncMock(return_value=[])):
            result = await run_research("What is revenue?", [], db_session)

        assert result.citations == []
        assert "not find" in result.answer.lower() or "relevant" in result.answer.lower()

    @pytest.mark.asyncio
    async def test_llm_failure_raises_runtime_error(self, db_session):
        from pydantic_ai.exceptions import UnexpectedModelBehavior

        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(side_effect=UnexpectedModelBehavior("bad"))

        with patch("app.agents.research_agent.retrieve", new=AsyncMock(return_value=[
            {"document_id": "doc-1", "chunk_index": 0, "text": "some text", "score": 0.9}
        ])):
            with patch("app.agents.research_agent._get_agent", return_value=mock_agent):
                with pytest.raises(RuntimeError):
                    await run_research("a question", ["doc-1"], db_session)


# ---------------------------------------------------------------------------
# comparison_agent
# ---------------------------------------------------------------------------

_FAKE_METRICS_A = FinancialMetrics(
    company="Acme Corp",
    quarter="Q1 2026",
    revenue="$4.2B",
    growth="+12% YoY",
    guidance="$4.5B next quarter",
    risks=["supply chain disruption"],
)

_FAKE_METRICS_B = FinancialMetrics(
    company="Beta Inc",
    quarter="Q1 2026",
    revenue="$2.1B",
    growth="+5% YoY",
    guidance="$2.2B next quarter",
    risks=["regulatory risk"],
)


class TestRunComparison:
    def _make_comparison_result(self, doc_ids):
        return ComparisonResult(
            documents=[
                DocumentMetrics(document_id=doc_ids[0], metrics=_FAKE_METRICS_A),
                DocumentMetrics(document_id=doc_ids[1], metrics=_FAKE_METRICS_B),
            ],
            analysis="Acme Corp outperforms Beta Inc on revenue and growth.",
        )

    @pytest.mark.asyncio
    async def test_returns_comparison_result(self, db_session):
        doc_ids = ["doc-aaa", "doc-bbb"]

        mock_run = AsyncMock(return_value=MagicMock(
            output=self._make_comparison_result(doc_ids)
        ))
        mock_agent = MagicMock()
        mock_agent.run = mock_run

        with (
            patch("app.agents.comparison_agent._load_text", new=AsyncMock(return_value="some text")),
            patch("app.agents.comparison_agent.run_extraction", new=AsyncMock(side_effect=[_FAKE_METRICS_A, _FAKE_METRICS_B])),
            patch("app.agents.comparison_agent._get_agent", return_value=mock_agent),
        ):
            result = await run_comparison(doc_ids, db_session)

        assert isinstance(result, ComparisonResult)
        assert len(result.documents) == 2
        assert result.documents[0].metrics.company == "Acme Corp"
        assert result.documents[1].metrics.company == "Beta Inc"
        assert "Acme" in result.analysis

    @pytest.mark.asyncio
    async def test_fewer_than_two_ids_raises_value_error(self, db_session):
        with pytest.raises(ValueError, match="2 document"):
            await run_comparison(["only-one"], db_session)

    @pytest.mark.asyncio
    async def test_empty_document_uses_empty_metrics(self, db_session):
        """Documents with no chunks get empty FinancialMetrics without crashing."""
        doc_ids = ["doc-empty-1", "doc-empty-2"]

        mock_run = AsyncMock(return_value=MagicMock(
            output=ComparisonResult(
                documents=[
                    DocumentMetrics(document_id="doc-empty-1", metrics=FinancialMetrics()),
                    DocumentMetrics(document_id="doc-empty-2", metrics=FinancialMetrics()),
                ],
                analysis="No data available.",
            )
        ))
        mock_agent = MagicMock()
        mock_agent.run = mock_run

        with (
            patch("app.agents.comparison_agent._load_text", new=AsyncMock(return_value="")),
            patch("app.agents.comparison_agent._get_agent", return_value=mock_agent),
        ):
            result = await run_comparison(doc_ids, db_session)

        assert result.documents[0].metrics.company == ""
        assert result.documents[1].metrics.company == ""

    @pytest.mark.asyncio
    async def test_llm_failure_raises_runtime_error(self, db_session):
        from pydantic_ai.exceptions import UnexpectedModelBehavior

        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(side_effect=UnexpectedModelBehavior("fail"))

        with (
            patch("app.agents.comparison_agent._load_text", new=AsyncMock(return_value="text")),
            patch("app.agents.comparison_agent.run_extraction", new=AsyncMock(return_value=FinancialMetrics())),
            patch("app.agents.comparison_agent._get_agent", return_value=mock_agent),
        ):
            with pytest.raises(RuntimeError):
                await run_comparison(["doc-x", "doc-y"], db_session)
