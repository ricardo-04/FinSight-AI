"""
PDF -> Markdown parser using PyMuPDF.
"""
import fitz  # PyMuPDF

def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    return "\n\n".join(pages)
