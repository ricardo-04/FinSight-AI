---
name: api-contract-review
description: Compare backend API contracts with frontend API assumptions
argument-hint: "<endpoint-or-feature-scope>"
agent: story-qa-review
---

You are reviewing API contract consistency in SalesMate.

## Input

- Endpoint or feature scope: **${endpoint-or-feature-scope}**

## Workflow

1. Inventory related FastAPI routes and frontend API calls.
2. Compare paths, methods, query names, payloads, status codes, and error
   handling.
3. Check authentication and authorization expectations on both sides.
4. Identify contract drift and missing tests.

## Output

- Contract mismatches ordered by severity.
- Backend evidence.
- Frontend evidence.
- Required tests or documentation updates.