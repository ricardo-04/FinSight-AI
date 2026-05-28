"""
Tests for API endpoints: upload, extract, chat.
"""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# POST /api/upload/
# ---------------------------------------------------------------------------

class TestUploadEndpoint:
    @pytest.mark.asyncio
    async def test_rejects_non_pdf(self, client):
        response = await client.post(
            "/api/upload/",
            files={"file": ("test.txt", b"plain text", "text/plain")},
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_rejects_empty_file(self, client):
        response = await client.post(
            "/api/upload/",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_successful_upload_returns_document_id(self, client, sample_pdf_bytes):
        fake_id = str(uuid.uuid4())

        with patch(
            "app.api.upload.save_document",
            new=AsyncMock(return_value=fake_id),
        ):
            response = await client.post(
                "/api/upload/",
                files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
            )

        assert response.status_code == 201
        body = response.json()
        assert body["document_id"] == fake_id
        assert body["status"] == "ingested"

    @pytest.mark.asyncio
    async def test_parse_failure_returns_422(self, client, sample_pdf_bytes):
        with patch(
            "app.api.upload.save_document",
            new=AsyncMock(side_effect=ValueError("PDF contains no text.")),
        ):
            response = await client.post(
                "/api/upload/",
                files={"file": ("bad.pdf", sample_pdf_bytes, "application/pdf")},
            )

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/extract/{document_id}
# ---------------------------------------------------------------------------

class TestExtractEndpoint:
    @pytest.mark.asyncio
    async def test_returns_404_for_missing_document(self, client):
        with patch(
            "app.api.extract.get_document",
            new=AsyncMock(side_effect=ValueError("not found")),
        ):
            response = await client.post(f"/api/extract/{uuid.uuid4()}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_metrics_on_success(self, client, mock_llm_extraction):
        from app.agents.extraction_agent import FinancialMetrics
        from sqlalchemy.ext.asyncio import AsyncSession

        doc_id = str(uuid.uuid4())

        with patch("app.api.extract.get_document", new=AsyncMock(return_value={"id": doc_id, "filename": "report.pdf", "created_at": None})):
            with patch("app.api.extract.AsyncSessionLocal") as mock_session_cls:
                mock_session = MagicMock()
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock(return_value=False)
                mock_result = MagicMock()
                mock_result.fetchall.return_value = [MagicMock(text="chunk text")]
                mock_session.execute = AsyncMock(return_value=mock_result)
                mock_session_cls.return_value = mock_session

                with patch("app.api.extract.run_extraction", new=AsyncMock(return_value=mock_llm_extraction)):
                    response = await client.post(f"/api/extract/{doc_id}")

        assert response.status_code == 200
        body = response.json()
        assert "metrics" in body
        assert body["metrics"]["company"] == "Acme Corp"


# ---------------------------------------------------------------------------
# POST /api/chat/
# ---------------------------------------------------------------------------

class TestChatEndpoint:
    @pytest.mark.asyncio
    async def test_empty_question_returns_400(self, client):
        response = await client.post("/api/chat/", json={"question": "", "document_ids": []})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_whitespace_question_returns_400(self, client):
        response = await client.post("/api/chat/", json={"question": "   ", "document_ids": []})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_successful_chat_returns_answer_and_citations(self, client, mock_llm_research):
        from app.agents.research_agent import Citation, ResearchResult

        with patch("app.api.chat.run_research", new=AsyncMock(return_value=mock_llm_research)):
            response = await client.post(
                "/api/chat/",
                json={"question": "What was Acme revenue?", "document_ids": []},
            )

        assert response.status_code == 200
        body = response.json()
        assert "answer" in body
        assert isinstance(body["citations"], list)

    @pytest.mark.asyncio
    async def test_llm_failure_returns_500(self, client):
        with patch("app.api.chat.run_research", new=AsyncMock(side_effect=RuntimeError("LLM failed"))):
            response = await client.post(
                "/api/chat/",
                json={"question": "What is revenue?", "document_ids": []},
            )

        assert response.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/compare/
# ---------------------------------------------------------------------------

class TestCompareEndpoint:
    @pytest.mark.asyncio
    async def test_single_document_returns_400(self, client):
        response = await client.post(
            "/api/compare/",
            json={"document_ids": [str(uuid.uuid4())]},
        )
        # Pydantic min_length=2 fires before our code → 422 Unprocessable Entity
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_document_ids_returns_400(self, client):
        response = await client.post(
            "/api/compare/",
            json={"document_ids": []},
        )
        # Pydantic min_length=2 validation → 422
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_successful_compare_returns_analysis(self, client):
        from app.agents.comparison_agent import ComparisonResult, DocumentMetrics
        from app.agents.extraction_agent import FinancialMetrics

        doc_a = str(uuid.uuid4())
        doc_b = str(uuid.uuid4())

        fake_result = ComparisonResult(
            documents=[
                DocumentMetrics(document_id=doc_a, metrics=FinancialMetrics(company="Acme")),
                DocumentMetrics(document_id=doc_b, metrics=FinancialMetrics(company="Beta")),
            ],
            analysis="Acme outperforms Beta.",
        )

        with patch("app.api.compare.run_comparison", new=AsyncMock(return_value=fake_result)):
            response = await client.post(
                "/api/compare/",
                json={"document_ids": [doc_a, doc_b]},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["analysis"] == "Acme outperforms Beta."
        assert len(body["documents"]) == 2

    @pytest.mark.asyncio
    async def test_llm_failure_returns_500(self, client):
        with patch(
            "app.api.compare.run_comparison",
            new=AsyncMock(side_effect=RuntimeError("LLM failed")),
        ):
            response = await client.post(
                "/api/compare/",
                json={"document_ids": [str(uuid.uuid4()), str(uuid.uuid4())]},
            )

        assert response.status_code == 500
