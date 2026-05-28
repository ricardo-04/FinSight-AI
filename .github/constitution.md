# Project Constitution - FinSight AI

This document defines the non-negotiable rules for every agent, persona, and task in this repository.
Every agent must read this file before taking any action. Rules here take precedence over individual agent instructions.

---

## Identity and Language

- All code, comments, documentation, and agent outputs must be in English.
- Every response must start with the active persona name: `<Persona name>. <Response content>`

---

## Git Safety Rules (Non-negotiable)

- NEVER run `git commit`, `git push`, `git merge`, `git rebase`, `git tag`, `git reset --hard`, or `git push --force` unless the user explicitly requests it in the same message.
- When a commit is requested, follow `.github/git-commit-instructions.md`.
- Never bypass pre-commit hooks with `--no-verify`.

---

## Code Quality Non-negotiables

- Follow Clean Code and SOLID principles.
- All changes must compile and all unit tests must pass before declaring a task complete.
- No breaking public API changes unless explicitly required.
- Prefer minimal, coherent diffs. No drive-by refactors.
- Do not introduce new external dependencies without user confirmation.
- If a change requires editing files outside those explicitly requested, ask the user before proceeding.
- Type hints are mandatory on all Python function signatures.
- Never log credentials, tokens, secrets, or PII.

---

## File Write Safety

- Orchestrators apply all file changes directly using their own tools after receiving research or plans from subagents.
- File writes via `runSubagent` do not work. Subagents invoked through `runSubagent` are stateless. Never delegate file creation or editing to a subagent via `runSubagent`.
- Implementer agents invoked directly in VS Code apply all file changes using their own edit tools.

---

## Security Non-negotiables

- Follow OWASP Top 10 principles at all times.
- Never hardcode API keys, secrets, or credentials. Always use environment variables.
- Validate all inputs at API boundaries (FastAPI request models, Next.js API routes).
- Never expose internal error details to API consumers - log server-side only.
- Use parameterized queries or ORM abstractions; never build raw SQL from user input.
- LLM prompt inputs must be sanitized to prevent prompt injection.

---

## AI and RAG Conventions

- Always stream LLM responses where the API supports it.
- Every LLM call must pass through the `llm_provider.py` abstraction; never call the OpenAI client directly outside that module.
- All agent tools must be registered via PydanticAI's tool mechanism.
- Embeddings are always generated through `rag/embeddings.py`; never inline embedding calls.
- Chunk size and overlap must come from config, never be hardcoded in parsing modules.

---

## Observability

- Every new service method or agent run must emit an OpenTelemetry span.
- Trace context must be propagated across async boundaries.
- Never use `print()` for application logging; always use the `logging` module.

---

## Persona and Response Rules

- Personas must change mid-task when work crosses a technology boundary.
- Every agent response must begin with the active persona name.
- Read `.github/instructions/` for the relevant technology before starting any task.
