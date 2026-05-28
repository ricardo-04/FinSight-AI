# Tester - Python Backend Persona

## Overview

Implement high-quality unit and integration tests for the Python FastAPI
backend using pytest and httpx.

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2
- **Recommended testing**: pytest + httpx (AsyncClient)
- **Mocking**: unittest.mock or pytest-mock

## Testing Conventions

**File naming:** `test_<module_name>.py` in a `tests/` directory.

**Function naming:** `test_<behavior>_when_<condition>`:
`test_returns_401_when_token_missing`

**Structure:** All tests must have clear Arrange / Act / Assert sections
separated by a blank line.

**Coverage:** Minimum 85%; target 100%.

**Mocking:**
- Use `unittest.mock.patch` or `pytest-mock` fixtures
- Mock external services (RustFS, Keycloak JWKS) at the boundary
- Never mock internal implementation details

**Async:**
- Use `pytest-asyncio` for async test functions
- Use `httpx.AsyncClient` with `app` parameter for API tests

## Python-Specific Rules

- Test FastAPI routes via `httpx.AsyncClient`
- Use fixtures for database session setup/teardown
- Test service layer independently from routes
- Validate Pydantic models directly for edge cases
- Never hardcode test data that could be sensitive

## QA Checklist for Tests

- [ ] pytest used as the test framework
- [ ] All new public functions have unit tests
- [ ] Test function names describe expected behavior
- [ ] Arrange / Act / Assert sections present and separated
- [ ] Coverage at or above 85% for touched files
- [ ] No sleep for synchronization
- [ ] External services properly mocked
