---
applyTo: "backend/tests/**,frontend/**/*.test.*,frontend/**/*.spec.*"
---

# Instructions - Testing

## Overview

Both backend and frontend have their own test suites. Every code change must include corresponding test updates.

## Backend Testing (pytest)

### Framework and Libraries

- `pytest` with `pytest-asyncio` for async tests.
- `httpx.AsyncClient` (with `ASGITransport`) for endpoint integration tests.
- Use `pytest.fixture` for shared setup (DB session, test client, sample documents).

### Test Structure

```
backend/tests/
  __init__.py
  test_health.py
  test_upload.py       - upload endpoint integration tests
  test_extract.py      - extraction agent and endpoint tests
  test_chat.py         - chat/RAG endpoint tests
  test_parsing.py      - pdf_parser and chunker unit tests
  test_rag.py          - embedding and retrieval unit tests
  test_agents.py       - agent unit tests with mocked LLM
```

### Backend Conventions

- Test file naming: `test_<module>.py`.
- Test function naming: `test_<scenario>_<expected_outcome>`.
- Mock all LLM calls using `unittest.mock.AsyncMock`; never make real API calls in tests.
- Mock the database session for unit tests; use a test database (SQLite in-memory or test Postgres) for integration tests.
- Use `@pytest.mark.asyncio` on all async test functions.
- Every new public function in `agents/`, `rag/`, `parsing/`, `services/`, and `tools/` requires at least one happy-path and one error-path test.

### Coverage Targets

- Minimum 80% line coverage on `agents/`, `rag/`, `parsing/`, and `tools/`.
- Critical paths (extraction response validation, retrieval score filtering) must have explicit edge-case tests.

## Frontend Testing (Jest + React Testing Library)

### Framework and Libraries

- `jest` + `@testing-library/react` + `@testing-library/user-event`.
- Mock `fetch` or `axios` calls; never make real network requests in tests.

### Test Conventions

- Co-locate tests next to the component: `Button.tsx` and `Button.test.tsx` in the same folder.
- Test user-visible behavior, not implementation details.
- At minimum: renders without crashing, displays loading state, displays error state, displays data state.

## Test Data

- Use realistic but fake financial data in fixtures (e.g., sample revenue figures, company names like "Acme Corp Q1 2024").
- Never use real company names or real financial data as test fixtures.
- Do not commit real PDF files to the repository; use a small synthetic test PDF in `backend/tests/fixtures/`.
