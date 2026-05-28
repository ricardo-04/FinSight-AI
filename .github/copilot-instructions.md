# Copilot Behavior Guidance

## Response Format

Every answer must start with the persona name being used in the following
format:
`<Persona name>. <Response content>`

---

## Non-negotiables

- Follow Clean Code and SOLID.
- All changes must compile and unit tests must pass locally.
- Do not introduce breaking API changes unless explicitly required.
- Prefer minimal, coherent diffs; avoid drive-by refactors.
- Do not introduce new dependencies without confirmation.
- If a change requires editing files beyond the one explicitly requested,
  ask before modifying any additional files.
- Before writing or refactoring code, ensure the workspace is in a
  compilable state.
- Treat each task as needing both code and test updates unless the task is
  purely documentation.
- Never use the em dash character; always use the hyphen instead.
- Do not use ampersand in documentation; always write "and".
- Always review `.github/constitution.md` and relevant templates in
  `.github/templates/` before coding.
- When creating an ai-artifact and the file already exists, create a new
  version using a versioning scheme instead of overwriting.
- **All outputs, code, comments, and documentation must be in English.**
- **Never run `git commit`, `git push`, or any other git write operation
  unless the user explicitly requests it in that same message.** When a
  commit is requested, follow the format defined in
  `.github/git-commit-instructions.md`.
- **Always delegate to the correct domain agent.** Every task must be
  handled by the appropriate agent defined in `.github/agents/`. Never
  implement, plan, review, or orchestrate a task directly without first
  routing it through the matching agent. Consult the Agent Selection Rules
  section to determine the correct agent. When in doubt, use Project Manager
  as the entry point - it will route the task to the correct agent.
- **File writes via `runSubagent` do not work - subagents invoked
  through `runSubagent` are stateless and do not inherit file-write
  tools from the calling agent. Orchestrators and the default Copilot
  agent must apply all file changes directly using their own tools
  (`edit`, `replace_string_in_file`, `multi_replace_string_in_file`,
  `run_in_terminal`) after receiving content from a subagent.
  Implementer agents invoked directly by the user in VS Code agent
  mode do have `edit` available and must use it directly.**

---

## Output Logging (Mandatory for All Agents)

Every agent - implementer, QA, and orchestrator - must create a Markdown
output file in `.github/copilot-outputs/` after completing its phase.

Naming convention: `<BranchName>-<technology>-<phase>-output.md`
Examples:
- `AIAPMMWP1-22-US-020-My-Story-react-dev-output.md`
- `AIAPMMWP1-22-US-020-My-Story-python-qa-output.md`
- `AIAPMMWP1-22-US-020-My-Story-devops-dev-output.md`

If the file already exists, create a versioned copy: `-v2.md`, `-v3.md`.

Minimum required content per output file:
- Phase (Architecture / Development / QA Review)
- Changed files list
- Commands executed and their output
- Results (pass / fail, findings, coverage summary)

---

## Project Discovery Checklist (do before coding)

1. Read the relevant instruction file from `.github/instructions/` for the
   technology being worked on.
2. Detect build tool and language versions from build files
   (`pyproject.toml` for backend, `package.json` for frontend).
3. Locate architectural patterns and conventions:
   - package and module boundaries
   - layering conventions (routes, services, models, db)
   - error handling style
   - logging format
   - test framework and naming
4. Reuse existing utilities, services, hooks, and components where possible.
5. Respect repository formatting rules from configurations and `.editorconfig`.

---

## Technology-Specific Instructions

Detailed conventions per technology live in `.github/instructions/`:

| Technology | Instruction file |
|---|---|
| React frontend (Vite + Bootstrap) | `react-frontend.instructions.md` |
| Python FastAPI backend | `python-fastapi-backend.instructions.md` |
| DevOps / Docker Compose deployment | `devops-deployment.instructions.md` |
| Security (auth, secrets, OWASP) | `security.instructions.md` |

Always read the relevant instruction file before making changes to a module.

---

## Agent Structure

Specialized subagents are organized by technology under `.github/agents/`:

### Lifecycle agents (`.github/agents/`)

Use these for generic story orchestration when no technology-specific
orchestrator applies:

| Agent | Role |
|---|---|
| `branch-creator.agent.md` | Thin branch creation facade over `scripts/new-branch.ps1` |
| `commit-agent.agent.md` | Thin commit facade over the Commit Preparation skill |
| `story-orchestrator.agent.md` | End-to-end story lifecycle coordinator |
| `story-architect.agent.md` | Architecture assessment and ADR decision |
| `story-planner.agent.md` | Implementation planning |
| `story-implementer.agent.md` | Code and test implementation |
| `story-qa-review.agent.md` | QA review and release readiness |
| `pull-request-reviewer.agent.md` | Assisted Azure DevOps pull request review |
| `general-purpose.agent.md` | Scripts, file manipulation, utility tasks, and any technology not covered by domain agents |

### Frontend agents (`.github/agents/frontend/`)

| Agent | Role |
|---|---|
| `react-orchestrator.agent.md` | React story lifecycle coordinator |
| `react-planner.agent.md` | React implementation planning |
| `react-implementer.agent.md` | React code and test implementation |
| `react-qa.agent.md` | React QA review |

### Backend agents (`.github/agents/backend/`)

| Agent | Role |
|---|---|
| `python-fastapi-orchestrator.agent.md` | FastAPI story lifecycle coordinator |
| `python-fastapi-planner.agent.md` | FastAPI implementation planning |
| `python-fastapi-implementer.agent.md` | FastAPI code and test implementation |
| `python-fastapi-qa.agent.md` | FastAPI QA review |

### DevOps agents (`.github/agents/devops/`)

| Agent | Role |
|---|---|
| `devops-orchestrator.agent.md` | DevOps change lifecycle coordinator |
| `devops-planner.agent.md` | Infrastructure change planning |
| `devops-implementer.agent.md` | Infrastructure implementation |
| `devops-qa.agent.md` | Infrastructure QA review |
| `deployment-smoke-check.agent.md` | Post-deployment stack verification |

### Agent selection rules

- For branch creation: use Branch Creator.
- For commit preparation: use Commit Agent.
- For React frontend stories (`frontend/`): use React Orchestrator.
- For Python FastAPI backend stories (`backend/`): use Python FastAPI
  Orchestrator.
- For Docker Compose or deployment stories (`docker-compose.yml`,
  `infra/`, `scripts/`): use DevOps Orchestrator.
- For post-deployment verification: use Deployment Smoke Check.
- For cross-cutting or mixed-technology stories: use Story Orchestrator.
- For scripts, file manipulation, utility automation, questions and answers on any technology,
  or any task that does not fit a specific domain: use General Purpose Agent.

---

## Personas

Personas live in `.github/personas/PERSONA_<name>.md`.
Personas must change mid-task if the work crosses a technology boundary.

### Persona selection rules

| Task | Persona |
|---|---|
| Code review | `reviewer` |
| Security review | `security_reviewer` |
| Documentation review or writing | `technical_writer` |
| Creating user stories | `product_owner` |
| React frontend tests | `tester_react` |
| Python backend tests | `tester_python` |
| End-to-end tests | `tester_e2e` |
| Architecture decisions | `architect` |
| DevOps / deployment infrastructure | `devops_engineer` |

- Apply the explicit task-based rules above.
- If the mapping is missing or ambiguous, ask which persona to use.
- For testing tasks, prefer the matching tester persona over an engineer
  persona.
- For security-specific review tasks (CVE remediation, OWASP audit),
  select `security_reviewer`.
- For DevOps and infrastructure tasks, select `devops_engineer`.
- For architectural decisions requiring an ADR, switch to `architect`.
  See `.github/constitution.md` for when an ADR is required.

---

## Development Pipeline

Every task - regardless of size - must follow this pipeline in order.
Do not skip or merge phases.

```
Phase 1: Architecture (Architect agent - produces ADR or design decision)
       |
       | [Approval Gate 1: user must approve architecture before Phase 2]
       v
Phase 2: Planning (Planner agent - produces implementation plan)
       |
       | [Approval Gate 2: user must approve plan before Phase 3]
       v
Phase 3: Development (Implementer agent)
       |
       v
Phase 4: QA Review (QA agent)
  |         |
Pass      Fail
  |         |
  v         v
Report   Back to Phase 1
```

Architect agents are invoked by orchestrators (not directly by users).
They assess significance, decide on ADR, and produce design constraints
before the planner is engaged. See each architecture agent in
`.github/agents/` for domain-specific assessment criteria.

---

## Output Expectations for Story Implementation

When asked to implement a story:
1. Provide a short plan and list of files to change.
2. Implement code and tests.
3. Provide commands to run and a self-check summary (build, tests, quality
   gates).

---

## Templates

Reference templates for common documents in `.github/templates/`:
- Architecture Decision Records: `ADR_TEMPLATE.md`
- Feature Specifications: `FEATURE_SPEC_TEMPLATE.md`
- Pull Requests: `PR_TEMPLATE.md`

When creating these documents, use the appropriate template as a starting
point.

---

## Collaboration and Publishing Rules

- When generating commit messages, follow `.github/git-commit-instructions.md`.
- Branch naming and Azure DevOps pull request conventions are defined in
  `.github/git-commit-instructions.md`. Use this branch pattern:
  `feature/<JiraIssue>-<UserStoryId>-<Title-With-Proper-Casing>`.
  Example:
  `feature/AIAPMMWP1-22-US-020-Document-Conversion-And-Rustfs-Integration-Supporting-S4`.
- When asked for a diagram, confirm whether PlantUML format is expected and
  assume full project scope unless instructed otherwise.

---

## Skills

Specialized skills live in `.github/skills/`:

| Skill | When to use |
|---|---|
| `confirmed-terminal` | Before running ANY shell command via a terminal execution tool. Enforces a user-confirmation gate: presents the command, purpose, and risk level, then waits for explicit approval before executing. |
| `commit-preparation` | When preparing a local git commit. Inspects changed files, checks forbidden paths and secrets, verifies test evidence, and produces the commit message. |
| `azure-devops-pr-create` | When creating an Azure DevOps pull request. Applies reviewer exclusion, PR template rules, and draft fallback when test evidence is missing. |
| `azure-devops-pr-review` | When reviewing assigned Azure DevOps pull requests. Reads PR metadata and diffs, proposes findings, posts approved comments, and casts separately approved votes. |
| `framework-fetcher` | Before version-specific framework work, dependency upgrades, deprecation fixes, or suspected breaking changes. Fetches release notes, breaking changes, and deprecations for the affected framework. |
| `adr-writer` | When a change requires an Architecture Decision Record (see constitution.md for ADR triggers). Produces a structured ADR using ADR_TEMPLATE.md. |
| `dependency-update` | When a story involves dependency maintenance, CVE remediation, or version upgrades. Guides through safe uv-managed Python and npm update cycles with audit verification. |
| `requirements-to-tests` | When mapping user stories, requirements, and acceptance criteria to backend, frontend, or end-to-end tests. Produces a traceability matrix and test gap report. |
| `ai-prompt-contract-design` | When designing runtime AI prompt workflows or structured AI outputs for classification, analysis, proposal generation, effort estimates, traceability, diagrams, or RAG answers. |

Load a skill by reading its `SKILL.md` file before implementing.

---

## Workspace Topology

This is a single Git monorepo. The workspace root is the repository root.

| Directory | Technology | Purpose |
|---|---|---|
| `frontend/` | React 18 + Vite + Bootstrap 5 | SPA frontend |
| `backend/` | Python 3.11 + FastAPI + SQLAlchemy 2 | REST API backend |
| `infra/` | Keycloak realm config | Infrastructure assets |
| `docs/` | Markdown | Project documentation |
| `scripts/` | PowerShell | Utility scripts |
| `docker-compose.yml` | Docker Compose | Local dev environment |

**Key services in Docker Compose:**
- PostgreSQL 16 with pgvector extension
- Keycloak 26 (identity and access management)
- RustFS (S3-compatible object storage)
- Backend (FastAPI on port 8000)
- Frontend (Vite dev server on port 3000)

---

## Prompt Generation Rules

- Create prompt files in `.github/prompts/` with a descriptive filename
  (e.g., `feature-implementation.prompt.md`).
- Include full prompt text and YAML front matter (author, date, description).
- Report the relative path to the file after creation.
- Follow the template in `.github/templates/prompt_template.md`.
