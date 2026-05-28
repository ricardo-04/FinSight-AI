"""
Tests for parsing/pdf_parser.py and parsing/chunker.py.
"""
import pytest

from app.parsing.chunker import chunk_text
from app.parsing.pdf_parser import ParsedDocument, parse_pdf


# ---------------------------------------------------------------------------
# pdf_parser
# ---------------------------------------------------------------------------

class TestParsePdf:
    def test_parse_bytes_returns_parsed_document(self, sample_pdf_bytes):
        result = parse_pdf(sample_pdf_bytes)
        assert isinstance(result, ParsedDocument)

    def test_parse_bytes_has_pages(self, sample_pdf_bytes):
        result = parse_pdf(sample_pdf_bytes)
        assert result.total_pages >= 1

    def test_parse_bytes_has_text(self, sample_pdf_bytes):
        result = parse_pdf(sample_pdf_bytes)
        assert len(result.full_text) > 0

    def test_parse_invalid_bytes_raises(self):
        with pytest.raises(Exception):
            parse_pdf(b"not a pdf")

    def test_parse_empty_bytes_raises(self):
        with pytest.raises(Exception):
            parse_pdf(b"")


# ---------------------------------------------------------------------------
# chunker
# ---------------------------------------------------------------------------

class TestChunkText:
    def test_basic_chunking_returns_list(self):
        text = " ".join(["word"] * 200)
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_chunk_size_respected(self):
        text = " ".join(["word"] * 300)
        chunks = chunk_text(text, chunk_size=50, overlap=0)
        # Each chunk should have at most 50 words
        for chunk in chunks:
            assert len(chunk.split()) <= 50

    def test_overlap_produces_shared_words(self):
        words = [f"w{i}" for i in range(20)]
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=10, overlap=3)
        # The last 3 words of chunk[0] should appear at start of chunk[1]
        last_words_first = chunks[0].split()[-3:]
        first_words_second = chunks[1].split()[:3]
        assert last_words_first == first_words_second

    def test_empty_text_returns_empty_list(self):
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            chunk_text("some text", chunk_size=0)

    def test_overlap_gte_chunk_size_raises(self):
        with pytest.raises(ValueError):
            chunk_text("some text", chunk_size=10, overlap=10)

    def test_short_text_returns_single_chunk(self):
        text = "short text here"
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0] == text
