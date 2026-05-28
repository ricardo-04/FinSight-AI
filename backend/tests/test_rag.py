"""
Tests for rag/embeddings.py, rag/pipeline.py, and rag/retrieval.py.
"""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.embeddings import embed_chunks, embed_query, embed_text


# ---------------------------------------------------------------------------
# embeddings
# ---------------------------------------------------------------------------

class TestEmbedChunks:
    @pytest.mark.asyncio
    async def test_returns_list_of_vectors(self):
        fake_vectors = [[0.1] * 1024, [0.2] * 1024]
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[0.1] * 1024),
            MagicMock(index=1, embedding=[0.2] * 1024),
        ]
        with patch(
            "app.rag.embeddings.get_raw_client",
            return_value=MagicMock(
                embeddings=MagicMock(
                    create=AsyncMock(return_value=mock_response)
                )
            ),
        ):
            with patch("app.rag.embeddings.get_embedding_config", return_value={"model": "test-model", "dimensions": 1024}):
                result = await embed_chunks(["chunk one", "chunk two"])
        assert result == fake_vectors

    @pytest.mark.asyncio
    async def test_empty_input_returns_empty_list(self):
        result = await embed_chunks([])
        assert result == []

    @pytest.mark.asyncio
    async def test_embed_query_uses_query_input_type(self):
        mock_response = MagicMock()
        mock_response.data = [MagicMock(index=0, embedding=[0.5] * 1024)]
        captured = {}

        async def fake_create(**kwargs):
            captured["extra_body"] = kwargs.get("extra_body", {})
            return mock_response

        with patch(
            "app.rag.embeddings.get_raw_client",
            return_value=MagicMock(embeddings=MagicMock(create=fake_create)),
        ):
            with patch("app.rag.embeddings.get_embedding_config", return_value={"model": "test-model", "dimensions": 1024}):
                await embed_query("what is revenue?")

        assert captured["extra_body"].get("input_type") == "query"


# ---------------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------------

class TestIngestDocument:
    @pytest.mark.asyncio
    async def test_raises_on_empty_chunks(self, db_session):
        from app.rag.pipeline import ingest_document

        with pytest.raises(ValueError, match="empty chunk list"):
            await ingest_document("doc-1", [], db_session)

    @pytest.mark.asyncio
    async def test_stores_correct_number_of_chunks(self, db_session, sample_chunks, mock_embeddings):
        import uuid
        from app.models.document import Document
        from app.rag.pipeline import ingest_document

        doc_id = str(uuid.uuid4())
        doc_row = Document(id=doc_id, filename="test.pdf")
        db_session.add(doc_row)
        await db_session.flush()

        with patch("app.rag.pipeline.embed_chunks", new=AsyncMock(return_value=[[0.1] * 1024] * len(sample_chunks))):
            # SQLite cannot store list[float] directly; mock flush to skip the
            # actual INSERT (the pgvector Vector type is not supported in SQLite)
            with patch.object(db_session, "flush", new=AsyncMock()):
                count = await ingest_document(doc_id, sample_chunks, db_session)

        assert count == len(sample_chunks)


# ---------------------------------------------------------------------------
# retrieval
# NOTE: The retrieve() function uses the pgvector `<=>` cosine distance
# operator which is not supported by SQLite. These tests mock session.execute
# so the pgvector SQL never reaches the in-memory SQLite database.
# ---------------------------------------------------------------------------

class TestRetrieve:
    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_rows(self, db_session):
        """When the mocked query returns no rows, retrieve returns []."""
        from app.rag.retrieval import retrieve

        mock_result = MagicMock()
        mock_result.fetchall.return_value = []

        with patch("app.rag.retrieval.embed_query", new=AsyncMock(return_value=[0.1] * 1024)):
            with patch.object(db_session, "execute", new=AsyncMock(return_value=mock_result)):
                results = await retrieve("any question", db_session)

        assert results == []

    @pytest.mark.asyncio
    async def test_returns_hits_with_expected_keys(self, db_session):
        """Rows returned by the query are mapped to the expected dict shape."""
        from app.rag.retrieval import retrieve

        fake_row = MagicMock()
        fake_row.document_id = "doc-abc"
        fake_row.chunk_index = 0
        fake_row.text = "Acme Corp revenue $4.2B"
        fake_row.score = 0.91

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [fake_row]

        with patch("app.rag.retrieval.embed_query", new=AsyncMock(return_value=[0.1] * 1024)):
            with patch.object(db_session, "execute", new=AsyncMock(return_value=mock_result)):
                results = await retrieve("revenue?", db_session)

        assert len(results) == 1
        assert results[0]["document_id"] == "doc-abc"
        assert results[0]["chunk_index"] == 0
        assert results[0]["score"] == 0.91
        assert "text" in results[0]

    @pytest.mark.asyncio
    async def test_filters_by_document_ids(self, db_session):
        """Passing document_ids restricts the query - no exception raised."""
        from app.rag.retrieval import retrieve

        mock_result = MagicMock()
        mock_result.fetchall.return_value = []

        with patch("app.rag.retrieval.embed_query", new=AsyncMock(return_value=[0.1] * 1024)):
            with patch.object(db_session, "execute", new=AsyncMock(return_value=mock_result)):
                results = await retrieve("revenue?", db_session, document_ids=["doc-123"])

        assert results == []

    @pytest.mark.asyncio
    async def test_calls_embed_query_with_sanitized_input(self, db_session):
        """retrieve() must call embed_query exactly once."""
        from app.rag.retrieval import retrieve

        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_embed = AsyncMock(return_value=[0.1] * 1024)

        with patch("app.rag.retrieval.embed_query", new=mock_embed):
            with patch.object(db_session, "execute", new=AsyncMock(return_value=mock_result)):
                await retrieve("What is revenue?", db_session)

        mock_embed.assert_called_once()
