---
applyTo: "docker-compose.yml,backend/Dockerfile,frontend/Dockerfile,docker/**"
---

# Instructions - DevOps and Docker Compose Deployment

## Overview

FinSight AI runs entirely via Docker Compose. No Kubernetes or cloud-native orchestration is used in the local development setup.

## Services

| Service | Image / Build | Port | Purpose |
|---|---|---|---|
| `backend` | `backend/Dockerfile` | 8000 | FastAPI app |
| `frontend` | `frontend/Dockerfile` | 3000 | Next.js app |
| `db` | `postgres:16-alpine` | 5432 | PostgreSQL 16 with pgvector |

## Key Commands

```bash
docker compose up --build          # full rebuild and start
docker compose up -d               # start in background
docker compose down                # stop and remove containers
docker compose down -v             # stop and remove containers + volumes (destructive)
docker compose logs -f backend     # tail backend logs
docker compose exec backend bash   # shell into backend container
```

## Environment Variables

All configuration is injected via a `.env` file at the project root. Never hardcode values.

Required variables:

```
OPENAI_API_KEY=
LLM_PROVIDER=openai          # openai | nim | ollama
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=                # required for nim and ollama
EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/finsight
CHUNK_SIZE=512
CHUNK_OVERLAP=64
RAG_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=0.75
MAX_PROMPT_INPUT_LENGTH=8000
```

## Dockerfile Rules

- Use multi-stage builds where applicable to minimize image size.
- Pin base image versions (e.g., `python:3.11-slim`, `node:20-alpine`).
- Do not copy `.env` or any secret file into the image.
- Run as a non-root user in production-like images.
- Backend: `COPY requirements.txt` and `RUN pip install` before copying app code (layer caching).

## Docker Compose Rules

- Use named volumes for persistent data (PostgreSQL data directory).
- Define a `healthcheck` on the `db` service so dependent services wait for readiness.
- Use `depends_on` with `condition: service_healthy` for backend and frontend.
- Never pin `latest` tags. Always specify exact or minor version tags.
- Use environment variable substitution (`${VAR}`) to avoid hardcoding values in `docker-compose.yml`.
