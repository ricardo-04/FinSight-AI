---
applyTo: "backend/**"
---

# Instructions - Python FastAPI Backend (backend/)

## Project Overview

Python 3.11 FastAPI backend providing REST API endpoints for the SalesMate
platform. Uses SQLAlchemy 2 for ORM, Alembic for migrations, PostgreSQL
with pgvector for persistence, boto3 for S3-compatible object storage
(RustFS), and PyJWT for Keycloak token validation.

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2
- **Migrations**: Alembic
- **Validation**: Pydantic (via FastAPI)
- **Auth**: PyJWT with Keycloak JWKS validation
- **Storage**: boto3 (S3-compatible RustFS)
- **Database**: PostgreSQL 16 with pgvector extension
- **Settings**: pydantic-settings
- **Server**: uvicorn
- **Testing**: Not yet configured (recommend pytest + httpx)

## Key Commands

```bash
cd backend
uv sync                                        # install all dependencies
uv sync --group dev                            # install with dev dependencies
uv run alembic upgrade head                    # run database migrations
uv run uvicorn app.main:app --reload           # start dev server on port 8000
uv run alembic revision --autogenerate -m "description"  # create migration
uv run pytest                                  # run tests
```

## Project Structure

```
backend/
  app/
    main.py              # FastAPI app, lifespan, CORS middleware
    api/
      routes.py          # API router with all endpoint definitions
      dependencies/
        auth.py          # JWT/Keycloak authentication dependency
    core/
      config.py          # Settings via pydantic-settings
    db/
      base.py            # SQLAlchemy declarative base
      models.py          # ORM model definitions
      session.py         # Database session factory
    services/
      opportunities.py   # Business logic for opportunities
      rustfs.py          # RustFS/S3 storage integration
  alembic/
    env.py               # Alembic environment configuration
    versions/            # Migration version scripts
  alembic.ini            # Alembic configuration
  pyproject.toml         # Project metadata and dependencies
  Dockerfile             # Container image definition
```

## Python Conventions

- Follow PEP 8 naming: snake_case for functions, variables, modules;
  PascalCase for classes; UPPER_SNAKE_CASE for constants
- Type hints on all function signatures
- Docstrings on public functions and classes (Google style)
- No wildcard imports; import specific names
- Remove unused imports after every change
- Use `logging` module: `logger = logging.getLogger(__name__)`
- Never log credentials, tokens, or PII
- No placeholder variable names (`foo`, `bar`, `temp`, `data`, etc.)

## FastAPI Conventions

- Single APIRouter in `app/api/routes.py` mounted on the app
- Use `Depends()` for dependency injection (auth, db sessions)
- Business logic in `app/services/` - route handlers are thin
- Request/response validation via Pydantic models
- Use appropriate HTTP status codes (201 for creation, 404 for not found)
- Async endpoints for I/O operations

## SQLAlchemy Conventions

- Declarative models inherit from `Base` in `app/db/base.py`
- Use `mapped_column()` with explicit types (SQLAlchemy 2 style)
- Relationships defined with `relationship()` and `ForeignKey`
- Session management via `SessionLocal` factory in `app/db/session.py`
- Never construct SQL via string concatenation; use ORM or parameterized
  queries only

## Alembic Migration Conventions

- Auto-generate migrations when models change
- Migration message must describe the change concisely
- Always review auto-generated migrations before committing
- Migration filenames follow the pattern: `NNNN_description.py`
- Test migrations in both directions (upgrade and downgrade)

## Configuration Conventions

- All configuration via `pydantic-settings` in `app/core/config.py`
- Environment variables for all values that change per environment
- Never hardcode database URLs, credentials, or service endpoints
- Use `${VAR:-default}` pattern in Docker for optional overrides

## Authentication Conventions

- JWT validation in `app/api/dependencies/auth.py`
- Fetch JWKS from Keycloak for signature verification
- Validate `iss`, `aud`, and `exp` claims
- Extract user roles from token claims
- Never validate tokens with string operations; use PyJWT library

## RustFS/S3 Storage Conventions

- Use boto3 with custom endpoint URL for RustFS
- Bucket bootstrap in `app/services/rustfs.py` at startup
- Configure endpoint via `RUSTFS_ENDPOINT` environment variable
- Use bucket/object prefixes for organizing opportunity files

## Security

- Follow OWASP Top 10 guidelines
- Never log sensitive data (tokens, passwords, PII)
- Validate and sanitize all external input at API boundaries
- Use Pydantic for input validation (automatic via FastAPI)
- Never hardcode secrets; always read from environment variables
- SQL injection prevention: use ORM or parameterized queries only

## Output Logging

After every implementation or QA review, create a Markdown file in
`.github/copilot-outputs/` named `<BranchName>-python-<phase>-output.md`.
If the file exists, create a versioned copy: `-v2.md`, `-v3.md`, etc.
The file must include: phase run, changed files, commands executed, and
results.

## Development Pipeline

Every task must follow this pipeline:
1. Architecture phase - produce a clear design decision
2. Development phase - implement following the architectural decision
3. QA Review phase - validate quality and release readiness

Use the Python FastAPI Orchestrator agent for end-to-end story
implementation.
