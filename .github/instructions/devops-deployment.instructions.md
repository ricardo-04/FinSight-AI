---
applyTo: "docker-compose.yml,infra/**,scripts/**,**/Dockerfile"
---

# Instructions - DevOps / Deployment Infrastructure

## Project Overview

Docker Compose-based local development environment for the SalesMate
platform. Includes PostgreSQL with pgvector, Keycloak for identity,
RustFS for S3-compatible object storage, a FastAPI backend, and a
Vite-based React frontend.

## Tech Stack

- **Orchestration**: Docker Compose v2
- **Database**: PostgreSQL 16 with pgvector extension
- **Identity**: Keycloak 26
- **Storage**: RustFS (S3-compatible)
- **Backend**: Python 3.11 FastAPI (Dockerfile in backend/)
- **Frontend**: Node 20 React/Vite (Dockerfile in frontend/)
- **Scripts**: PowerShell (scripts/)
- **Environment**: `.env` file for variable overrides

## Key Commands

```bash
docker compose up --build            # build and start all services
docker compose ps                    # check all service statuses
docker compose logs <service> --tail 50  # inspect logs for a service
docker compose down --remove-orphans # stop stack (keep volumes)
docker compose down --volumes        # stop and wipe all persistent data
```

## Service Inventory

| Container | Published Port | Image |
|---|---|---|
| `salesmate-postgres` | 55432 | pgvector/pgvector:pg16 |
| `salesmate-keycloak` | 8081 | quay.io/keycloak/keycloak:26.1.0 |
| `salesmate-rustfs` | 9010 (S3), 9011 (console) | rustfs/rustfs:latest-glibc |
| `salesmate-backend` | 18000 | Built from backend/Dockerfile |
| `salesmate-frontend` | 13000 | Built from frontend/Dockerfile |

## docker-compose.yml Conventions

- Every service must declare a `healthcheck` where feasible
- Services with runtime dependencies must use `depends_on: condition:
  service_healthy` (or `service_started` when healthcheck is not available)
- Persistent data must use named volumes declared in the top-level
  `volumes:` block; never bind-mount host paths for application data
- Environment variables that change between deployments must be
  parameterized with `${VAR:-default}` syntax
- Use YAML block scalars for long values to keep lines readable
- Place environment variables in alphabetical order within each service

## Dockerfile Conventions

- Pin base images to specific versions (e.g., `python:3.11-slim`,
  `node:20-alpine`); never use `:latest` for application images
- Minimize layers; combine related RUN commands
- Use `.dockerignore` to exclude unnecessary files
- COPY dependency manifests first, install, then copy source (layer
  caching)
- Set `WORKDIR` explicitly
- Expose only the required port

## Environment Variable Conventions

- All service configuration via environment variables
- Database credentials: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- Keycloak: `KEYCLOAK_ADMIN`, `KEYCLOAK_ADMIN_PASSWORD`, `KEYCLOAK_REALM`
- RustFS: `RUSTFS_ENDPOINT`
- Backend: `CORS_ORIGINS`, `KEYCLOAK_SERVER_URL`, `KEYCLOAK_PUBLIC_URL`
- Frontend (build args): `VITE_API_BASE_URL`, `VITE_KEYCLOAK_URL`,
  `VITE_KEYCLOAK_REALM`, `VITE_KEYCLOAK_CLIENT_ID`
- Never hardcode credentials in docker-compose.yml or Dockerfiles

## Keycloak Configuration

- Realm configuration exported to `infra/keycloak/realm-export.json`
- Imported at startup via `--import-realm` command
- Development mode (`start-dev`) - not for production
- Demo users defined in the realm export for local testing

## Security

- Follow OWASP Top 10 guidelines; never log sensitive data
- Never hardcode passwords or secrets in source files
- All credentials must come from environment variables
- Pin Docker base images to specific versions or digests

## Output Logging

After every implementation or QA review, create a Markdown file in
`.github/copilot-outputs/` named `<BranchName>-devops-<phase>-output.md`.
If the file exists, create a versioned copy: `-v2.md`, `-v3.md`, etc.
The file must include: phase run, changed files, commands executed, and
results.

## Development Pipeline

Every change must follow this pipeline:
1. Architecture phase - identify affected files and assess impact
2. Development phase - implement following the architectural decision
3. QA Review phase - validate correctness, idempotency, and security

Use the DevOps Orchestrator agent for end-to-end infrastructure changes.
