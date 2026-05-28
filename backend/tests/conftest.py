"""
Shared pytest fixtures for FinSight AI backend tests.

All database interactions use an in-memory SQLite database so tests run
without a running PostgreSQL instance. LLM and embedding calls are always
mocked - no real API calls are made in tests.
"""
import asyncio
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.main import app


# ---------------------------------------------------------------------------
# Event loop
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for the whole test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# In-memory SQLite async engine (replaces PostgreSQL in tests)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create all tables in an in-memory SQLite database."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        # pgvector Vector column is not supported by SQLite; patch it to Text
        # so the schema can be created without a real Postgres instance.
        from sqlalchemy import Text
        from app.models.document import DocumentChunk
        DocumentChunk.embedding.property.columns[0].type = Text()
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield a fresh async session for each test, rolled back on teardown."""
    TestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSession() as session:
        await session.begin()
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# HTTP test client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client pointed at the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Return a minimal real PDF (1 page, synthetic text) for parsing tests."""
    # Minimal valid PDF structure with a text stream
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 44 >>\nstream\n"
        b"BT /F1 12 Tf 100 700 Td (Acme Corp Q1 2026 Revenue $4.2B) Tj ET\n"
        b"endstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n9\n%%EOF"
    )


@pytest.fixture
def sample_chunks() -> list[str]:
    """Return a list of realistic synthetic financial text chunks."""
    return [
        "Acme Corp reported Q1 2026 revenue of $4.2 billion, up 12% year-over-year.",
        "Gross margin improved to 68% driven by product mix and operating leverage.",
        "Forward guidance for Q2 2026: revenue between $4.4B and $4.6B.",
        "Key risks include macroeconomic uncertainty and supply chain disruptions.",
    ]


@pytest.fixture
def mock_embeddings():
    """Patch embed_chunks and embed_query to return deterministic fake vectors."""
    fake_vector = [0.1] * 1024
    with (
        patch("app.rag.embeddings.embed_chunks", new=AsyncMock(return_value=[[0.1] * 1024] * 10)),
        patch("app.rag.embeddings.embed_query", new=AsyncMock(return_value=fake_vector)),
        patch("app.rag.pipeline.embed_chunks", new=AsyncMock(return_value=[[0.1] * 1024] * 10)),
    ):
        yield fake_vector


@pytest.fixture
def mock_llm_extraction():
    """Patch the extraction agent to return a fixed FinancialMetrics result."""
    from app.agents.extraction_agent import FinancialMetrics
    from unittest.mock import MagicMock

    fake_metrics = FinancialMetrics(
        company="Acme Corp",
        quarter="Q1 2026",
        revenue="$4.2B",
        growth="+12% YoY",
        guidance="Q2 2026 revenue $4.4B-$4.6B",
        risks=["Macroeconomic uncertainty", "Supply chain disruptions"],
    )
    mock_result = MagicMock()
    mock_result.output = fake_metrics

    with patch(
        "app.agents.extraction_agent._get_agent",
        return_value=MagicMock(run=AsyncMock(return_value=mock_result)),
    ):
        yield fake_metrics


@pytest.fixture
def mock_llm_research():
    """Patch the research agent to return a fixed ResearchResult."""
    from app.agents.research_agent import Citation, ResearchResult
    from unittest.mock import MagicMock

    fake_result = ResearchResult(
        answer="Acme Corp reported Q1 2026 revenue of $4.2B, up 12% YoY. [1]",
        citations=[
            Citation(
                document_id="doc-123",
                chunk_index=0,
                snippet="Acme Corp reported Q1 2026 revenue of $4.2 billion",
            )
        ],
    )
    mock_result = MagicMock()
    mock_result.output = fake_result

    with patch(
        "app.agents.research_agent._get_agent",
        return_value=MagicMock(run=AsyncMock(return_value=mock_result)),
    ):
        yield fake_result
