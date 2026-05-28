# Skills Portfolio Assessment - Technical Writer Review

**Phase:** Planning / Review
**Date:** 2026-05-12
**Persona:** Technical Writer

---

## Scope

Review of `.github/` customization improvements requested through a
skills portfolio assessment. No files were edited. This document
is the implementation checklist for the development phase.

---

## Files to Change

### 1. `.github/skills/dependency-update/SKILL.md` - EDIT

Replace all `pip`-only commands with `uv`-aware equivalents and align
the frontend verification steps to scripts that exist in
`package.json`.

Changes required:

- Step 1 - replace `pip list --outdated` with `uv pip list --outdated`
- Step 2 - replace `pip audit` with `uvx pip-audit`
- Step 4 - replace `pip install -e ".[dev]"` with `uv sync --group dev`
  and `pytest` with `uv run pytest`
- Step 4 frontend - the `package.json` defines `build` but no `test`
  script; replace the implicit test step with `npm run build` and
  `npm audit --audit-level=high` only (no `npm test`)
- YAML `description` field - update to mention `uv` alongside `pip`

Risk: LOW - documentation-only change; does not affect runtime code.

---

### 2. `.github/skills/framework-fetcher/SKILL.md` - EDIT

Narrow activation. The current YAML `description` ends with "or any
other technology in the project" which causes the skill to trigger on
every dependency task. The body condition list also says "any of the
following conditions" with an open-ended fourth bullet.

Changes required:

- Remove "or any other technology in the project" from the YAML
  `description` field; replace it with "Use only for the named
  frameworks in the project: React, FastAPI, SQLAlchemy, Vite,
  Keycloak, Alembic, Pydantic."
- Remove or tighten the fourth trigger bullet ("agent is implementing a
  feature where the API changed between versions") to require an
  explicit version mismatch signal, not just any feature work
- Retain the full step-by-step procedure and URL table unchanged

Risk: LOW - may cause under-triggering for unlisted packages such as
`pgvector` or `boto3`. Accept this trade-off by noting those
packages in a "Scope" callout within the skill.

---

### 3. `.github/skills/adr-writer/SKILL.md` - EDIT

Remove the Maven example from the ADR-required-when list. This is a
Python/React project with no Java or Maven dependency.

Changes required:

- Line 25: change
  "Introduces a new external dependency (Maven, npm, Docker image)"
  to
  "Introduces a new external dependency (pip/uv, npm, Docker image)"

Risk: NONE - cosmetic accuracy fix.

---

### 4. `.github/skills/confirmed-terminal/SKILL.md` - EDIT

Remove Maven and `mvn` references from the description, keywords,
and risk table. Replace with project-accurate equivalents. The
detailed confirmation gate procedure must remain unchanged.

Changes required:

- YAML `description` line 6: remove "Maven," from the example list
- YAML `keywords` line 8: remove "maven,"
- Risk table LOW row: replace `` `mvn test` `` with `` `uv run pytest` ``
- Risk table MEDIUM row: replace `` `mvn package` `` with
  `` `uv sync --group dev` ``

Risk: NONE - cosmetic accuracy fix; no procedural change.

---

### 5. `.github/skills/requirements-to-tests/SKILL.md` - CREATE NEW

New skill: guides agents from user story or requirement text to
concrete test cases and test code.

Minimum required content:
- YAML frontmatter: `name`, `description`, and `keywords` covering
  "user story to tests", "acceptance criteria", "test generation",
  "BDD", "pytest", "vitest", "test cases"
- Step 1: extract acceptance criteria from the story
- Step 2: classify tests (unit, integration, end-to-end)
- Step 3: map each criterion to a named test function
- Step 4: produce test stubs following the project test conventions
  (pytest for backend, Vitest for frontend when added)
- Step 5: link back to story ID in test docstring or comment
- Output section: summary table of criteria to test names

Risk: MEDIUM - needs alignment with the tests.instructions.md
conventions. Read `.github/instructions/tests.instructions.md`
before drafting the skill body to avoid contradictions.

---

### 6. `.github/skills/ai-prompt-contract-design/SKILL.md` - CREATE NEW

New skill: defines a structured process for designing, versioning, and
validating AI prompt contracts used by agents in this project.

Minimum required content:
- YAML frontmatter: `name`, `description`, and `keywords` covering
  "prompt design", "prompt contract", "system prompt", "agent prompt",
  "prompt template", "LLM instructions"
- Step 1: define the prompt purpose and target agent/model
- Step 2: identify required input variables and output format
- Step 3: draft the prompt using `.github/templates/prompt_template.md`
- Step 4: validate against the output contract (schema or example)
- Step 5: version the prompt file in `.github/prompts/`
- Output section: prompt file path and a one-sentence contract summary

Risk: LOW - purely additive; no impact on existing agents.

---

### 7. `.github/copilot-instructions.md` - EDIT

Register both new skills in the Skills table so agents can discover
them via semantic search.

Changes required:

- Add a row for `requirements-to-tests` with the description:
  "When a user story or requirement must be translated into test cases
  or test code stubs."
- Add a row for `ai-prompt-contract-design` with the description:
  "When designing, versioning, or validating AI prompt templates or
  agent instruction contracts."

Risk: LOW - additive table change only.

---

## Summary Table

| # | File | Action | Risk |
|---|---|---|---|
| 1 | `.github/skills/dependency-update/SKILL.md` | Edit | LOW |
| 2 | `.github/skills/framework-fetcher/SKILL.md` | Edit | LOW |
| 3 | `.github/skills/adr-writer/SKILL.md` | Edit | NONE |
| 4 | `.github/skills/confirmed-terminal/SKILL.md` | Edit | NONE |
| 5 | `.github/skills/requirements-to-tests/SKILL.md` | Create | MEDIUM |
| 6 | `.github/skills/ai-prompt-contract-design/SKILL.md` | Create | LOW |
| 7 | `.github/copilot-instructions.md` | Edit | LOW |

---

## Risks and Mitigations

**R1 - uv not installed in the dev environment.**
The dependency-update skill will reference `uv` and `uvx` commands.
If the dev container or CI environment does not have `uv` installed,
the commands will fail. Mitigation: add an environment pre-check note
in the skill ("Verify `which uv` before running these steps.").

**R2 - framework-fetcher under-triggering after narrowing.**
Packages like `pgvector`, `boto3`, and `python-multipart` will not
appear in the named list. Agents may skip version checks for those
packages. Mitigation: add a "Packages not listed here" callout in
Step 1 that instructs agents to still apply the skill for any
installed package that shows a build failure or deprecation warning.

**R3 - requirements-to-tests conflicts with tests.instructions.md.**
The new skill must match the test file naming, fixture, and assertion
conventions already defined in the instruction file.
Mitigation: read `tests.instructions.md` before drafting
the skill body and cross-reference it explicitly in the skill.

**R4 - new skills not discovered by agents.**
Skills are selected by semantic similarity from the `copilot-
instructions.md` table. If the keyword coverage in the new skill
descriptions is too narrow, agents will not invoke them.
Mitigation: choose keywords matching the user-facing request language
("generate tests from story", "design prompt", "acceptance criteria").

---

## Not in Scope

- No changes to agent files under `.github/agents/`.
- No changes to `ADR_TEMPLATE.md` (it contains no Maven references).
- No changes to backend or frontend source code.
- No new npm or pip dependencies introduced.
