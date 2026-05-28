---
applyTo: "backend/app/agents/**,backend/app/rag/**,backend/app/tools/**,backend/app/services/llm_provider.py"
---

# Instructions - AI and RAG Layer

## Overview

FinSight AI's intelligence layer consists of three agents, an embedding and retrieval pipeline, and a set of tools. All AI work must follow these conventions in addition to the general Python FastAPI backend rules.

## Agent Architecture

```
agents/
  extraction_agent.py   - extracts structured FinancialMetrics from document chunks
  research_agent.py     - answers user questions via RAG over ingested documents
  comparison_agent.py   - compares metrics across multiple documents
tools/
  calculator.py         - financial ratio and formula tool
  sec_fetch.py          - fetches filings from SEC EDGAR API
  vector_search.py      - similarity search tool used by agents
rag/
  embeddings.py         - generates and stores embeddings
  pipeline.py           - end-to-end document ingest pipeline
  retrieval.py          - pgvector retrieval with score thresholds
services/
  llm_provider.py       - provider abstraction for OpenAI / NVIDIA NIM / Ollama
```

## LLM Provider Rules

- All LLM calls must go through `llm_provider.py`. It reads `LLM_PROVIDER`, `LLM_MODEL`, and `LLM_BASE_URL` from environment.
- Supported provider values: `openai`, `nim`, `ollama`.
- Never instantiate `openai.AsyncOpenAI` or any LLM client outside `llm_provider.py`.

## PydanticAI Agent Rules

- Define structured output models in the same file as the agent or in `models/`.
- Use `@agent.tool` to register tools. Tool functions must be `async def` and must have type hints and docstrings.
- Agents must set a `system_prompt` that clearly instructs the LLM on output format.
- Always handle `ModelRetry` exceptions from PydanticAI and log the retry attempt.
- Validate all structured outputs with Pydantic; if the LLM response does not conform, raise a clear error and log the raw response (but not user data if sensitive).

## Extraction Agent Rules

- Input: raw markdown text from a parsed PDF chunk.
- Output: `FinancialMetrics` Pydantic model with fields: `company`, `quarter`, `revenue`, `growth`, `guidance`, `risks`.
- Use the extraction prompt from `docs/prompts/extraction_prompt.md`.
- On extraction failure, log the error with the chunk index and document ID, and return a partially filled model rather than raising.

## Research Agent Rules

- Input: user question + list of document IDs.
- Output: answer string + list of citation objects (document ID, chunk index, text snippet).
- Retrieve top-K chunks via `rag/retrieval.py` before calling the LLM.
- Do not exceed the configured `RAG_TOP_K` environment variable for retrieval.
- Include citations in the response; never fabricate references.

## Comparison Agent Rules

- Input: two or more document IDs + list of metric keys to compare.
- Output: structured comparison table with delta values and trend indicators.
- Must call the extraction agent per document to get normalized metrics before comparing.

## RAG Pipeline Rules

- Pipeline order: upload -> parse (PyMuPDF) -> chunk -> embed -> store in pgvector.
- Each step must emit an OpenTelemetry span with document ID as an attribute.
- Chunk size defaults to `CHUNK_SIZE` env var (default 512 tokens); overlap defaults to `CHUNK_OVERLAP` (default 64).
- Embedding model is set by `EMBEDDING_MODEL` env var; default `text-embedding-3-small`.
- Store embeddings as `vector(1536)` (or the correct dimension for the configured model).

## Retrieval Rules

- Use cosine similarity (`<=>` pgvector operator).
- Apply a `RETRIEVAL_SCORE_THRESHOLD` (default 0.75) to filter low-quality results.
- Always return document ID, chunk index, score, and text snippet per result.

## Tool Conventions

- Every tool function must be `async def`.
- Tools must validate their inputs and raise `ValueError` with a clear message on invalid input.
- The `sec_fetch` tool must respect rate limits; use exponential backoff on 429 responses.
- The `calculator` tool must return results as strings with units; never return raw floats to the agent.

## Prompt Injection Prevention

- All user-provided text passed to LLM prompts must be sanitized:
  - Strip leading/trailing whitespace.
  - Truncate to a maximum of `MAX_PROMPT_INPUT_LENGTH` characters (default 8000).
  - Remove null bytes and non-printable control characters.
- Never construct prompts by direct f-string interpolation of untrusted input into the system prompt section.
