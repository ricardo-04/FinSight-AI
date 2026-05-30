"""
PDF to markdown parser using PyMuPDF (fitz).

Converts each page to plain text, preserving paragraph structure.
Returns both the full concatenated text and per-page metadata so
downstream chunks can carry accurate source references.
"""
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# Hard cap on pages parsed, to bound CPU/memory against decompression-bomb PDFs.
_MAX_PAGES: int = int(os.getenv("PDF_MAX_PAGES", "1500"))


@dataclass
class ParsedDocument:
    """Result of parsing a PDF file."""

    filename: str
    total_pages: int
    full_text: str
    pages: list[dict]  # [{"page": int, "text": str}]


def parse_pdf(source: str | bytes | Path) -> ParsedDocument:
    """Parse a PDF file or bytes object into a ParsedDocument.

    Args:
        source: File path (str or Path) or raw PDF bytes.

    Returns:
        A ParsedDocument with full text and per-page breakdown.

    Raises:
        ValueError: If the source is not a valid PDF, is encrypted, has too many
            pages, or contains no extractable text.
    """
    if isinstance(source, (str, Path)):
        filename = Path(source).name
        try:
            doc = fitz.open(str(source))
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Could not open PDF '{filename}': {exc}") from exc
    else:
        filename = "<bytes>"
        try:
            doc = fitz.open(stream=source, filetype="pdf")
        except Exception as exc:  # noqa: BLE001 - malformed/corrupt bytes
            raise ValueError(f"Could not open PDF '{filename}': {exc}") from exc

    # Reject encrypted/password-protected PDFs rather than emitting garbage.
    if getattr(doc, "needs_pass", False) or getattr(doc, "is_encrypted", False):
        doc.close()
        raise ValueError(f"PDF '{filename}' is encrypted and cannot be processed.")

    if doc.page_count == 0:
        doc.close()
        raise ValueError(f"PDF '{filename}' contains no pages.")

    if doc.page_count > _MAX_PAGES:
        page_count = doc.page_count
        doc.close()
        raise ValueError(
            f"PDF '{filename}' has {page_count} pages, exceeding the {_MAX_PAGES}-page limit."
        )

    pages: list[dict] = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        # Replace multiple blank lines with a single separator
        text = re.sub(r"\n{3,}", "\n\n", text)
        pages.append({"page": page_num, "text": text})

    doc.close()

    non_empty = [p for p in pages if p["text"]]
    if not non_empty:
        raise ValueError(f"PDF '{filename}' contains no extractable text.")

    full_text = "\n\n".join(p["text"] for p in non_empty)

    logger.info(
        "Parsed PDF: filename=%s pages=%d chars=%d",
        filename,
        len(pages),
        len(full_text),
    )

    return ParsedDocument(
        filename=filename,
        total_pages=len(pages),
        full_text=full_text,
        pages=pages,
    )
