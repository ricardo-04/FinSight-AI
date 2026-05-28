---
name: requirements-to-tests
description: >-
  Maps SalesMate user stories, acceptance criteria, and requirements into
  concrete backend pytest, frontend Vitest, and end-to-end test plans. Use
  this skill when generating tests from a story, validating acceptance
  criteria, building a traceability matrix, or reviewing test gaps.
  Keywords: user story to tests, acceptance criteria, test generation,
  BDD, pytest, Vitest, traceability, coverage gap.
---

# Requirements To Tests Skill

## Purpose

SalesMate stories are acceptance-criteria driven. This skill turns user
stories, requirements, and implementation evidence into a precise test
traceability plan before tests are written or reviewed.

Use it when the user asks to generate tests, validate a story against its
acceptance criteria, or assess test coverage for a planned or implemented
change.

---

## Step 1: Gather Product Evidence

Read the smallest useful set of evidence:
- `docs/user-stories.csv` for story title, dependencies, and acceptance
  criteria.
- `docs/requirements.md` for functional and non-functional requirements.
- `docs/user-story-status-matrix.md` when implementation state matters.
- `.github/instructions/tests.instructions.md` for test conventions.
- `backend/pyproject.toml` and `frontend/package.json` for available
  test tooling.

If the story ID is missing or ambiguous, ask the user for the story ID
before producing a matrix.

---

## Step 2: Extract Acceptance Criteria

For each acceptance criterion, capture:
- The user-visible behavior or system invariant.
- The affected layer: backend, frontend, AI, DevOps, integration, or
  documentation.
- Required authorization, validation, persistence, and error behavior.
- External systems that must be mocked at their boundary.

Do not invent acceptance criteria. Mark gaps as assumptions and request
confirmation if they affect implementation.

---

## Step 3: Choose Test Levels

Map each criterion to the lowest useful test level:
- Backend pytest for API behavior, persistence, auth, validation, and
  service logic.
- Frontend Vitest and React Testing Library for screens, routing,
  interactions, loading states, and errors when tooling is configured.
- Integration or smoke checks for cross-service flows.
- Manual validation only when tooling is not configured or the external
  dependency is unavailable.

If frontend test tooling is not configured, do not claim executable
frontend tests exist. Record a tooling gap and use `npm run build` as the
available frontend validation check.

---

## Step 4: Build The Traceability Matrix

Use `.github/skills/requirements-to-tests/templates/acceptance-test-matrix.md`
as the matrix template.

Every row must include:
- Story ID.
- Acceptance criterion.
- Test layer.
- Planned test file.
- Test name or validation action.
- Required mocks, fixtures, or seed records.
- Current status: planned, implemented, missing, blocked, or manual.

---

## Step 5: Generate Or Review Tests

When asked to generate tests:
- Follow `.github/instructions/tests.instructions.md`.
- Use descriptive test names such as
  `test_returns_unauthorized_when_token_is_missing`.
- Mock Keycloak JWKS, RustFS, network clients, and browser fetch calls at
  their boundaries.
- Assert response bodies, status codes, authorization behavior, and UI
  states explicitly.

When asked to review tests:
- Confirm every changed behavior has coverage or a documented limitation.
- Flag missing tests by acceptance criterion, not by file alone.

---

## Output Format

Produce a requirements-to-tests report with:

1. **Scope:** story IDs, requirements, and changed modules reviewed.
2. **Traceability matrix:** one row per acceptance criterion.
3. **Test files to add or update:** path, purpose, and owner layer.
4. **Mocks and fixtures:** boundary mocks and seed records required.
5. **Tooling gaps:** missing test runners, coverage tools, or services.
6. **Validation plan:** commands or manual checks available in the repo.
