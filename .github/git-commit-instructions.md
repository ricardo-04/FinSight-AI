# Git Commit Instructions - FinSight AI

## Commit Message Format

Use Conventional Commits:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

## Types

| Type | When to use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or correcting tests |
| `docs` | Documentation only changes |
| `chore` | Build process, dependency updates, tooling |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |

## Scopes

Use one of the following scopes to identify the affected module:

| Scope | Covers |
|---|---|
| `backend` | FastAPI app, general backend changes |
| `agents` | extraction_agent, research_agent, comparison_agent |
| `rag` | embeddings, pipeline, retrieval |
| `parsing` | pdf_parser, chunker |
| `api` | health, upload, extract, chat endpoints |
| `db` | models, migrations, session |
| `services` | document_service, llm_provider |
| `tools` | calculator, sec_fetch, vector_search |
| `telemetry` | OpenTelemetry setup |
| `frontend` | Next.js app, components, pages |
| `infra` | Docker Compose, Dockerfiles |
| `docs` | Documentation files |
| `tests` | Test files |

## Rules

- Subject line: imperative mood, no period, max 72 chars.
- Body: explain WHY, not what. Wrap at 72 chars.
- Reference tasks or issues in the footer: `Closes #123`
- Never use the em dash; use a hyphen instead.
- Never use ampersand; write "and" instead.

## Examples

```
feat(rag): add pgvector cosine similarity retrieval

Implements similarity search using pgvector's <=> operator.
Replaces the previous in-memory numpy cosine computation,
reducing memory footprint on large document sets.

Closes #42
```

```
fix(agents): handle empty extraction response from LLM

The extraction agent previously raised an unhandled KeyError
when the LLM returned a response missing the `revenue` field.
Added a fallback to empty string with a warning log.
```

```
chore(infra): pin postgres image to 16-alpine
```
