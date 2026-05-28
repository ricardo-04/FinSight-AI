---
applyTo: "backend/**"
---

# Instructions - Python FastAPI Backend (backend/)

## Project Overview

Python 3.11 FastAPI backend for FinSight AI. Provides REST endpoints for PDF upload, financial metric extraction, RAG-based chat, and document management. Uses SQLAlchemy 2 and asyncpg for async PostgreSQL access, pgvector for similarity search, PydanticAI for LLM agent orchestration, and PyMuPDF for PDF parsing.

## Tech Stack

| Component | Library / Version |
|---|---|
| Language | Python 3.11 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2 (async) |
| Database driver | asyncpg |
| Validation | Pydantic v2 |
| AI agents | PydanticAI |
| LLM client | openai (OpenAI-compatible) |
| PDF parsing | PyMuPDF (fitz) |
| Vector store | pgvector |
| Observability | OpenTelemetry |
| Testing | pytest + pytest-asyncio + httpx |

## Key Commands

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload         # start dev server on port 8000
pytest                                 # run tests
```

## Project Structure

```
backend/app/
  main.py              - FastAPI app, CORS middleware, router registration
  agents/
    extraction_agent.py  - structured metric extraction via LLM
    research_agent.py    - RAG-based Q&A with citations
    comparison_agent.py  - multi-document comparison
  api/
    health.py            - GET /health
    upload.py            - POST /api/upload
    extract.py           - POST /api/extract
    chat.py              - POST /api/chat
  db/
    base.py              - SQLAlchemy declarative base
    session.py           - async session factory
  models/
    document.py          - Document ORM model
    metrics.py           - FinancialMetrics ORM model
  parsing/
    pdf_parser.py        - PyMuPDF PDF-to-markdown parser
    chunker.py           - text chunker with configurable size and overlap
  rag/
    embeddings.py        - embedding generation (OpenAI embeddings API)
    pipeline.py          - end-to-end ingest pipeline
    retrieval.py         - pgvector similarity retrieval
  services/
    document_service.py  - document CRUD and processing orchestration
    llm_provider.py      - LLM provider abstraction (OpenAI / NVIDIA NIM / Ollama)
  telemetry/
    setup.py             - OpenTelemetry SDK setup
  tools/
    calculator.py        - financial calculator tool
    sec_fetch.py         - SEC EDGAR document fetcher
    vector_search.py     - vector search tool for agents
```

## Python Conventions

- PEP 8 naming: `snake_case` for functions, variables, modules; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants.
- Type hints on all function signatures - mandatory.
- Docstrings on all public functions and classes (Google style).
- No wildcard imports; import specific names.
- Remove unused imports after every change.
- Use `logging` module: `logger = logging.getLogger(__name__)`.
- Never log credentials, tokens, API keys, or PII.
- No placeholder variable names (`foo`, `bar`, `temp`, `data`).

## FastAPI Conventions

- All request and response bodies use Pydantic v2 models.
- All route handlers are `async def`.
- HTTP status codes: 200 for success, 201 for creation, 400 for client errors, 422 for validation errors, 500 for server errors.
- Use `HTTPException` with clear detail messages for error responses - never expose stack traces.
- Router files define a single `router = APIRouter()` and are registered in `main.py`.

## Database Conventions

- Use async SQLAlchemy sessions from `db/session.py`.
- Never use `session.execute(text(...))` with string interpolation.
- Use ORM models defined in `models/` for all database interactions.
- Database access belongs in service layer (`services/`), not in route handlers.

## AI Agent Conventions

- All LLM calls must go through `services/llm_provider.py`. Never call the OpenAI client directly outside that module.
- Use PydanticAI's structured output to validate LLM responses against Pydantic models.
- Sanitize all user-provided text before constructing LLM prompts (strip control characters, limit length).
- Agent tools must be registered via PydanticAI's `@agent.tool` decorator.
- All agent runs must emit an OpenTelemetry span.

## RAG Conventions

- Embeddings are always generated through `rag/embeddings.py`.
- Chunk configuration (size, overlap) comes from environment variables, never hardcoded.
- Retrieval results must include document ID and chunk index for citation purposes.

## Security Rules

- All API inputs must be validated by Pydantic models at the route boundary.
- File uploads: validate MIME type and file size before processing.
- Never store raw user input in the database without sanitization.
- Environment variables for all secrets (`OPENAI_API_KEY`, `DATABASE_URL`, etc.).
