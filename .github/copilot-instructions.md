# Copilot Behavior Guidance - FinSight AI

## Response Format

Every answer must start with the persona name being used in the following format:
`<Persona name>. <Response content>`

---

## Non-negotiables

- Follow Clean Code and SOLID principles.
- All changes must compile and unit tests must pass locally.
- Do not introduce breaking API changes unless explicitly required.
- Prefer minimal, coherent diffs; avoid drive-by refactors.
- Do not introduce new dependencies without confirmation.
- If a change requires editing files beyond the one explicitly requested, ask before modifying any additional files.
- Before writing or refactoring code, ensure the workspace is in a compilable state.
- Treat each task as needing both code and test updates unless the task is purely documentation.
- Never use the em dash character; always use the hyphen instead.
- Do not use ampersand in documentation; always write "and".
- Always review `.github/constitution.md` before coding.
- When creating an ai-artifact and the file already exists, create a new version using a versioning scheme instead of overwriting.
- **All outputs, code, comments, and documentation must be in English.**
- **Never run `git commit`, `git push`, or any other git write operation unless the user explicitly requests it in that same message.** When a commit is requested, follow the format defined in `.github/git-commit-instructions.md`.
- **Always delegate to the correct domain agent.** Every task must be handled by the appropriate agent defined in `.github/agents/`. Consult the Agent Selection Rules section below.
- **File writes via `runSubagent` do not work.** Orchestrators and the default Copilot agent must apply all file changes directly using their own tools after receiving content from a subagent.

---

## Project Overview

FinSight AI is an AI-powered financial intelligence platform for ingesting financial PDFs (earnings reports, SEC filings, presentations), extracting structured metrics with LLMs, and enabling RAG-based financial analysis.

### Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 + TailwindCSS |
| Backend | FastAPI (Python 3.11) |
| AI Layer | PydanticAI + OpenAI-compatible endpoints |
| Database | PostgreSQL 16 + pgvector |
| PDF Parsing | PyMuPDF (fitz) |
| Observability | OpenTelemetry |
| Infrastructure | Docker Compose |

### Key Modules

```
backend/app/
  agents/          - extraction_agent, research_agent, comparison_agent
  api/             - health, upload, extract, chat endpoints
  db/              - SQLAlchemy base, session factory
  models/          - document, metrics ORM models
  parsing/         - pdf_parser (PyMuPDF), chunker
  rag/             - embeddings, pipeline, retrieval
  services/        - document_service, llm_provider
  telemetry/       - OpenTelemetry setup
  tools/           - calculator, sec_fetch, vector_search
frontend/app/      - Next.js app router pages
frontend/components/ - React components
```

---

## Project Discovery Checklist (do before coding)

1. Read the relevant instruction file from `.github/instructions/` for the technology being worked on.
2. Detect language versions from build files (`requirements.txt` for backend, `package.json` for frontend).
3. Locate architectural patterns and conventions: module boundaries, layering (api, agents, services, models, db), error handling style.
4. Reuse existing utilities, services, hooks, and components where possible.
5. Respect repository formatting rules.

---

## Technology-Specific Instructions

Detailed conventions per technology live in `.github/instructions/`:

| Technology | Instruction file |
|---|---|
| Python FastAPI backend | `python-fastapi-backend.instructions.md` |
| Next.js frontend | `nextjs-frontend.instructions.md` |
| AI and RAG layer | `ai-rag.instructions.md` |
| DevOps / Docker Compose | `devops-deployment.instructions.md` |
| Security (OWASP) | `security.instructions.md` |
| Testing | `tests.instructions.md` |
| Git workflow | `git-workflow.instructions.md` |

Always read the relevant instruction file before making changes to a module.

---

## Agent Structure

Specialized subagents are organized by technology under `.github/agents/`:

### Lifecycle agents (`.github/agents/`)

| Agent | Role |
|---|---|
| `general-purpose.agent.md` | Scripts, file manipulation, utility tasks, ad-hoc work |
| `project-manager.agent.md` | Routes tasks to the correct domain agent |
| `story-orchestrator.agent.md` | End-to-end story lifecycle coordinator |
| `story-architect.agent.md` | Architecture assessment and ADR decisions |
| `story-planner.agent.md` | Implementation planning |
| `story-implementer.agent.md` | Code and test implementation |
| `story-qa-review.agent.md` | QA review and release readiness |

### Backend agents (`.github/agents/backend/`)

| Agent | Role |
|---|---|
| `python-fastapi-orchestrator.agent.md` | FastAPI story lifecycle coordinator |
| `python-fastapi-planner.agent.md` | FastAPI implementation planning |
| `python-fastapi-implementer.agent.md` | FastAPI code and test implementation |
| `python-fastapi-qa.agent.md` | FastAPI QA review |

### Frontend agents (`.github/agents/frontend/`)

| Agent | Role |
|---|---|
| `nextjs-orchestrator.agent.md` | Next.js story lifecycle coordinator |
| `nextjs-planner.agent.md` | Next.js implementation planning |
| `nextjs-implementer.agent.md` | Next.js code and test implementation |
| `nextjs-qa.agent.md` | Next.js QA review |

---

## Agent Selection Rules

- For Python FastAPI backend stories (`backend/`): use Python FastAPI Orchestrator.
- For Next.js frontend stories (`frontend/`): use Next.js Orchestrator.
- For AI/RAG layer changes (`backend/app/agents/`, `backend/app/rag/`): use Python FastAPI Orchestrator, but also read `ai-rag.instructions.md`.
- For infrastructure changes (`docker-compose.yml`, `Dockerfile`): use the General Purpose agent.
- For cross-cutting stories touching multiple layers: use Story Orchestrator.
- For unknown or general tasks: use Project Manager as entry point.

---

## Output Logging (Mandatory)

Every agent must create a Markdown output file in `.github/copilot-outputs/` after completing its phase.

Naming convention: `<feature-slug>-<technology>-<phase>-output.md`

Minimum required content:
- Phase (Architecture / Development / QA Review)
- Changed files list
- Commands executed and their output
- Results (pass / fail, findings, coverage summary)
