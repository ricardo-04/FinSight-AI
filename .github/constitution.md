# Project Constitution

This document defines the non-negotiable rules that apply to every agent,
persona, and task in this repository. Every agent must read this file
before taking any action. Rules here take precedence over individual agent
instructions where they conflict.

---

## Identity and Language

- All code, comments, documentation, and agent outputs must be in English.
- Every response must start with the active persona name in the format:
  `<Persona name>. <Response content>`
- Follow style and formatting rules in
  `.github/instructions/style.instructions.md`.

---

## Git Safety Rules (Non-negotiable)

- NEVER run `git commit`, `git push`, `git merge`, `git rebase`,
  `git tag`, `git reset --hard`, or `git push --force` unless the user
  explicitly requests it in the same message.
- When a commit is requested, follow `.github/git-commit-instructions.md`.
- Never bypass pre-commit hooks with `--no-verify`.

---

## Code Quality Non-negotiables

- Follow Clean Code and SOLID principles.
- All changes must compile and all unit tests must pass before declaring
  a task complete.
- No breaking public API changes unless explicitly required by the story.
- Prefer minimal, coherent diffs. No drive-by refactors.
- Do not introduce new external dependencies without user confirmation.
- If a change requires editing files outside those explicitly requested,
  ask the user before proceeding.

---

## File Write Safety

- Implementer agents invoked directly in VS Code apply all file changes
  using their own edit tools.
- Orchestrators apply all file changes directly using their own tools
  after receiving research or plans from subagents.
- File writes via `runSubagent` do not work. Subagents invoked through
  `runSubagent` are stateless. Never delegate file creation or editing
  to a subagent via `runSubagent`.

---

## Persona and Response Rules

- Personas must change mid-task when work crosses a technology boundary.
- Every agent response must begin with the active persona name.
- Read `.github/instructions/` for the relevant technology
  before starting any task.

---

## Output Logging (Mandatory for All Agents)

Every agent must create a Markdown output file in
`.github/copilot-outputs/` after completing its phase.

Naming convention: `<BranchName>-<technology>-<phase>-output.md`

If the file already exists, create a versioned copy: `-v2.md`, `-v3.md`.

Minimum required content:
- Phase (Architecture / Development / QA Review)
- Changed files list
- Commands executed and their output
- Results (pass / fail, findings, coverage summary)

---

## Phase Logging Format (Mandatory for All Agents)

Every agent must print a standardized phase banner at the start and end
of its response. Orchestrators must also log every delegation and receipt.
See the respective orchestrator agent files in `.github/agents/` for the
exact banner format and handoff log patterns.

### Phase Numbers by Role

| Phase | Name | Agent Role |
|---|---|---|
| 1 | Architecture | Architect |
| 2 | Planning | Planner |
| 3 | Development | Implementer |
| 4 | QA Review | QA |

---

## Security Non-negotiables

- Never log credentials, tokens, PII, or key material.
- Never hardcode secrets in source files, configuration templates, or
  Dockerfiles. Always read from environment variables or Docker secrets.
- All network sockets must use TLS 1.2 or higher.
- Certificate validation and hostname verification must never be disabled.
- Validate all inputs at system boundaries.
- XML parsers must be hardened against XXE injection.
- Follow OWASP Top 10 guidelines at all times.

---

## Documentation

- Every code change must also update related documentation: README,
  architecture docs, configuration guides, and inline comments.
- Treat missing documentation updates as a finding in QA review,
  with severity proportional to the scope of the change.

---

## Architecture Decision Records

An Architecture Decision Record (ADR) is required whenever a change:
- Introduces a new integration pattern or external dependency
- Changes a public API or module boundary
- Adds a new service, container, or infrastructure component
- Introduces a new architectural pattern not already used in the module

When an ADR is required, use `.github/templates/ADR_TEMPLATE.md`.
Place ADRs in `docs/architecture/decisions/`.

ADR assessment is the responsibility of the Architect agent (Phase 1)
in the 4-phase pipeline. Planners receive the ADR reference as input
from the orchestrator and must reference it in the plan preamble.
Planners do not produce ADRs.

---

## Approval Gates

The pipeline has two mandatory approval gates. Orchestrators must pause
and present the output to the user at each gate before proceeding.
The accepted approval phrases are: "approve", "proceed", or "yes".

- **Gate 1 (after Architecture)**: Present the architect's decision note
  or ADR and wait for user approval before delegating to the Planner.
- **Gate 2 (after Planning)**: Present the planning summary and wait for
  user approval before delegating to the Implementer.

---

## When the `architect` Persona Applies

Switch to the `architect` persona when:
- The change introduces a new service or module
- The story requires a new architectural pattern
- The change affects more than two modules simultaneously
- An ADR is required (see above)

---

## Project Discovery Checklist

Before any implementation, every agent must:

1. Read `.github/constitution.md` (this file)
2. Read `.github/copilot-instructions.md`
3. Read the relevant instruction file from `.github/instructions/`
4. Identify module boundaries, layering, and test conventions
5. Confirm build tool and language versions from build files
6. Reuse existing utilities, factories, mappers, validators, and fixtures
