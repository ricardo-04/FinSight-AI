# Architecture Overview

## High-Level Components

- **Frontend** (Next.js): PDF upload, chat UI, analysis dashboard
- **Backend** (FastAPI): auth, upload handling, agent orchestration, RAG endpoints
- **AI Layer**: Extraction Agent, Research Agent, Comparison Agent
- **Storage**: PostgreSQL (metadata + metrics) + pgvector (embeddings)
- **Observability**: OpenTelemetry traces, token metrics, latency

## LLM Provider Strategy

Provider abstraction supports OpenAI API, NVIDIA NIM, and local Ollama.
See `backend/app/services/llm_provider.py`.
