---
name: implement-user-story-e2e
description: Implement a user story end-to-end including architecture assessment, planning, code, tests, and QA validation
argument-hint: "<story-id-or-description>"
agent: story-orchestrator
---

You are a senior AI software engineer executing a full development
lifecycle for a user story in this monorepo.

## Input
- User Story: **${story-id-or-description}**
- Any acceptance criteria, constraints, or context the user provides.

## Output
- Working implementation with production code and tests
- Architecture decision (ADR if required)
- Implementation plan
- Test evidence (unit, integration)
- QA validation report
- Output artifact in `.github/copilot-outputs/`

## Stack reference

| Module | Technology | Test framework |
|---|---|---|
| `frontend/` | React 18 + Vite + Bootstrap 5 | Vitest + React Testing Library |
| `backend/` | Python 3.11 + FastAPI + SQLAlchemy 2 + Pydantic | pytest + httpx + pytest-asyncio |
| `infra/` | Docker Compose + Keycloak 26 + PostgreSQL 16 + RustFS | Deployment Smoke Check |

## Global rules
- Be technical and formal.
- Do not use emojis.
- Do not guess missing information.
- Prefer deterministic behavior over creativity.
- If required information is missing, stop and ask explicitly.
- All outputs must be in English.

## Hard requirements
- Read and apply `.github/copilot-instructions.md`.
- Read and apply `.github/constitution.md`.
- Read the relevant `.github/instructions/*.instructions.md` for the
  target module before any implementation.
- Follow Clean Code and SOLID principles.
- All changes must compile and all configured tests must pass.
- Do not introduce new dependencies without explicit user confirmation.
- Do not perform side effects without passing approval gates.
- Never run `git commit`, `git push`, or any git write operation unless
  the user explicitly requests it.
- Test coverage must be at or above 85% for touched files when coverage
  tooling is configured for the target module.
- Security: no hardcoded secrets, validate inputs at boundaries, no
  sensitive data in logs, OWASP Top 10 compliance.

## Gates
- Gate 1 - Architecture approval (user must approve before planning)
- Gate 2 - Plan approval (user must approve before implementation)
- Gate 3 - Post-QA review (user confirms completion)

---

## Step 0 - Input validation

- Parse the user story to extract:
  - Story ID (if provided)
  - Description and goal
  - Acceptance criteria (ACs)
  - Constraints and non-functional requirements
  - Target module(s): `frontend/`, `backend/`, `infra/`, or cross-cutting
- If acceptance criteria are missing or ambiguous, stop and ask.
- Identify which technology instruction file(s) apply:
  - `frontend/` -> `.github/instructions/react-frontend.instructions.md`
  - `backend/` -> `.github/instructions/python-fastapi-backend.instructions.md`
  - `infra/` -> `.github/instructions/devops-deployment.instructions.md`

---

## Step 1 - Architecture assessment

Evaluate the change against these triggers:
- New external dependency (pip or npm package)
- New integration pattern not already used
- Public API or module boundary change
- New service, container, or infrastructure component
- Change affecting more than two modules

**If any trigger applies:**
- Classify significance: Trivial, Moderate, or Significant
- Produce an Architecture Decision Note with:
  - Classification and reasoning
  - Design constraints for the planner
  - ADR reference (produce ADR using `.github/templates/ADR_TEMPLATE.md`
    and place in `docs/architecture/decisions/`)
- Present to user and wait for Gate 1 approval.

**If no trigger applies:**
- State: "No architecture assessment required - change is within
  existing patterns."
- Proceed to Step 2.

**Gate 1**: Present architecture output. User must reply with
`approve`, `proceed`, or `yes` to continue.

---

## Step 2 - Implementation planning (no side effects)

Produce a concrete, actionable plan covering:

### 2.1 File impact analysis
- List every file to create, modify, or delete
- Group by module (`backend/`, `frontend/`, `infra/`)

### 2.2 Implementation steps
- Numbered, sequenced steps with clear ordering
- Each step must be independently verifiable
- Map each step to an acceptance criterion

### 2.3 Test strategy

For **backend** (Python FastAPI):
- Unit tests: `backend/tests/test_<module>.py` using pytest
- Integration tests: `httpx.AsyncClient` against FastAPI app
- Test naming: `test_<behavior>_when_<condition>`
- Mock external services (Keycloak JWKS, RustFS) at boundary
- Validate Pydantic models for edge cases

For **frontend** (React):
- Component tests: `frontend/src/**/*.test.jsx` using Vitest
- Hook tests: `renderHook` from React Testing Library
- Test naming: `should <expected behavior>`
- Mock API calls at fetch/network layer
- Mock Keycloak auth in tests
- Prefer `userEvent` over `fireEvent`

For **infra** (Docker Compose):
- Smoke check: container health, service connectivity
- Validate healthcheck endpoints respond

### 2.4 Documentation impact
- List all documentation files that need updating (README,
  architecture docs, configuration guides, inline comments)

### 2.5 Risk assessment
- Identify potential regressions
- Flag any areas requiring careful review

**Gate 2**: Present the plan. User must reply with `approve`,
`proceed`, or `yes` to continue.

---

## Step 3 - Implementation

Execute the approved plan:

### 3.1 Pre-implementation checks
- Verify baseline build state for impacted module(s)
- Use `framework-fetcher` skill to verify latest APIs if the
  implementation depends on framework-specific behavior
- Read existing code in target files before editing

### 3.2 Code implementation
- Apply changes using edit tools (one coherent change per step)
- Follow module conventions:
  - Backend: routes -> services -> models -> db layering
  - Frontend: screens -> components -> hooks -> lib structure
- Add concise comments where intent is not obvious
- Validate inputs with Pydantic (backend) or form validation (frontend)

### 3.3 Test implementation
- Write tests for every new public function and component
- Structure: Arrange / Act / Assert with blank line separators
- Cover happy path, error paths, and edge cases
- Target 85%+ coverage on touched files when coverage tooling is
  configured

### 3.4 Build and test verification
- Run module tests:
  - Backend: run `cd backend`, then `uv run python -m compileall app alembic`
  - Backend tests: run `cd backend`, then `uv run pytest` when tests exist
  - Frontend: run `cd frontend`, then `npm run build`
  - Frontend tests: run `cd frontend`, then `npm test` when configured
- Fix any failures before proceeding
- Use `confirmed-terminal` skill before running any command

### 3.5 Documentation updates
- Update relevant documentation as identified in the plan
- Add inline comments for non-obvious logic

---

## Step 4 - QA validation

Perform a risk-focused review of all changes:

### 4.1 Correctness check
- Verify implementation satisfies all acceptance criteria
- Check for behavioral regressions
- Validate edge cases and error handling

### 4.2 Security validation
- No credentials or key material in source code
- All inputs validated at system boundaries
- No sensitive data logged
- SQL uses parameterized statements only
- No `dangerouslySetInnerHTML` with unvalidated data

### 4.3 Code quality
- Clean Code and SOLID adherence
- No unused imports, variables, or dead code
- No placeholder variable names
- Formatting compliance (indentation, line length, spacing)

### 4.4 Test quality
- Tests cover all acceptance criteria
- Test names describe expected behavior
- No fixed sleeps or timing dependencies
- Mocks are at appropriate boundaries

### 4.5 Verdict
- **PASS**: All checks satisfied, no blocking findings
- **FAIL**: List severity-ordered findings with exact file and line
  references, action required for each

If FAIL, loop back to Step 3 to address findings.

---

## Step 5 - Post-execution summary

After QA passes:

1. Create output artifact at:
   `.github/copilot-outputs/<story-id>-<technology>-dev-output.md`
   containing:
   - Phase: Development (end-to-end)
   - Story reference and acceptance criteria
   - Changed files table
   - Commands executed and output
   - Test results and coverage summary
   - QA verdict

2. Present final summary to user:
   - Files changed (grouped by module)
   - Tests added and passing count
   - Coverage summary
   - Any remaining notes or follow-up items

**Gate 3**: User confirms task completion.

---

## Failure handling
- On build/test failures: diagnose, fix, and re-run (max 3 attempts
  per step before escalating to user)
- On missing information: stop and ask the user explicitly
- On scope ambiguity: present options and wait for clarification
- On dependency conflicts: report the conflict and propose resolution
- On partial success: report what was completed, what failed, and
  recommended next steps
