---
applyTo: "backend/tests/**,frontend/src/**/*.test.jsx,frontend/src/**/*.spec.jsx"
---

# Instructions - Tests

## Scope

These rules apply to backend pytest tests and frontend Vitest tests.

## Backend Tests

- Use pytest.
- Name files `test_<module>.py`.
- Name tests `test_<behavior>_when_<condition>` when the condition is
  meaningful.
- Mock external systems at their boundary, including Keycloak JWKS,
  RustFS, and network clients.
- Assert HTTP status codes, response bodies, and security-sensitive
  behavior explicitly.

## Frontend Tests

- Use Vitest and React Testing Library.
- Name files `*.test.jsx` near the component under test.
- Prefer `userEvent` for interactions.
- Query by role, label, text, or accessible name.
- Mock API calls at the fetch or API utility boundary.

## Coverage

Coverage is required for touched behavior when the relevant tooling is
configured in project files. If tests or coverage tooling are not yet
configured, document the limitation in the output artifact and run the
available build or compile checks instead.