# FinSight AI

An AI-powered financial intelligence platform for ingesting financial PDFs (earnings reports, SEC filings, presentations), extracting structured metrics with LLMs, and enabling RAG-based financial analysis.

## Stack

- **Frontend**: Next.js + TailwindCSS
- **Backend**: FastAPI (Python)
- **AI Layer**: PydanticAI, OpenAI-compatible endpoints
- **Database**: PostgreSQL + pgvector
- **Observability**: OpenTelemetry
- **Infrastructure**: Docker Compose

## Quick Start

```bash
cp .env .env.local
# Fill in your API keys
docker-compose up --build
```

- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000  
- API Docs: http://localhost:8000/docs

## Features

- PDF upload and parsing (PyMuPDF → Markdown)
- Structured financial metric extraction (LLM → JSON)
- RAG chat with citations
- Multi-document comparison agent
- MCP-style tool orchestration
- Full OpenTelemetry tracing

## Architecture

See `docs/architecture/overview.md`.
