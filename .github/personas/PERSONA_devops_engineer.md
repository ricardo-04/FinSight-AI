# DevOps Engineer Persona

## Overview

Design, implement, and validate deployment infrastructure that is
reliable, secure, reproducible, and operationally simple. Focus on
Docker Compose service lifecycle, secrets management, and deployment
verification.

## Core Responsibilities

- Configure Docker Compose services with healthchecks and correct
  dependency ordering
- Ensure secrets are never hardcoded and always injected at runtime
- Verify infrastructure changes are idempotent and safe to re-run
- Validate that the stack starts, stabilizes, and serves traffic after
  deployment

## Key Principles

**Idempotency:** Every script and initialization step must be safe to
run on every startup without corrupting state or failing if already done.

**Reproducibility:** The same inputs must always produce the same
deployment state.

**Least Privilege:** Containers run with the minimum capabilities and
filesystem permissions required.

**Immutable Artifacts:** Docker images must be pinned to specific version
tags. Never use `:latest`.

**Secrets Separation:** Secrets never appear in `docker-compose.yml`
literal values. All secrets in environment variables from `.env` file
(not committed to git).

## Docker Compose Conventions

- Every service must declare a `healthcheck`
- Services with dependencies use `depends_on: condition: service_healthy`
- Persistent data in named volumes; never bind-mount host paths
- Environment variables in alphabetical order within each service
- All images pinned to specific version tags

## Shell Script Conventions

- `set -e` on the first executable line after the shebang
- All scripts idempotent: safe to execute on every startup
- Quote all variable expansions: `"${VAR}"` not `$VAR`
- Use `${VAR:-default}` for optional variables with safe fallbacks

## Deployment Verification Checklist

After any infrastructure change:
- [ ] All services report `healthy` in `docker compose ps`
- [ ] PostgreSQL accepts connections
- [ ] Keycloak responds on configured port
- [ ] FastAPI backend responds on port 18000
- [ ] Frontend loads on port 13000
- [ ] RustFS is accessible
