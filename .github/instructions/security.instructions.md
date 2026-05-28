---
applyTo: "**"
---

# Instructions - Security

## Scope

These rules apply to every module in the project: Python FastAPI backend,
React frontend, Docker Compose deployment, and all infrastructure
components. Security is non-negotiable and must be addressed in every
change that touches network communication, credentials, authentication,
or data handling.

---

## General Principles

- **Never hardcode credentials, passwords, key material, or tokens** in
  source files, configuration templates, or Dockerfiles. Always read them
  from environment variables or Docker secrets at runtime.
- **Never log credentials, tokens, PII, or key material.** Apply this rule
  in every `logger.*` call in Python and every `console.*` call in the
  frontend.
- **OWASP Top 10 compliance is required** for all production code.
- **Never commit `.env` files.** Ensure `.env` is in `.gitignore`.
- **Never disable TLS certificate verification** in production code
  (`verify=False` in httpx/requests, `"secure": false` in proxy config).

---

## FastAPI Backend - Authentication and Authorization

- Use OAuth 2.0 Authorization Code Flow with PKCE for browser clients.
  Never use the Implicit Flow.
- Validate the JWT signature, `iss`, `aud`, and `exp` claims in every
  protected endpoint. Use `python-jose` or `PyJWT` with JWKS fetching.
- Never validate tokens manually with string operations; always use a
  proper JWT library.
- Store tokens only in memory on the frontend. Never in `localStorage`
  for tokens with long expiry.
- Use FastAPI `Depends()` for auth injection. Never check auth inline in
  route handlers.

---

## FastAPI Backend - Input Validation

- Validate all inputs at the system boundary using Pydantic models.
- Never construct SQL queries by concatenating user-supplied strings.
  Use SQLAlchemy ORM or parameterized queries exclusively.
- Use `@validator` or `@field_validator` for complex validation logic.
- Apply `max_length`, `ge`, `le`, and `regex` constraints on Pydantic
  fields for all user-facing inputs.

---

## FastAPI Backend - HTTPS and CORS

- Configure CORS with explicit allowed origins. Never use `allow_origins=["*"]`
  in production.
- In production, run behind a TLS-terminating reverse proxy (e.g., Nginx,
  Traefik). The backend itself may listen on HTTP internally.
- Set `Secure`, `HttpOnly`, and `SameSite=Strict` on any cookies.

---

## React Frontend - Content Security

- Never use `dangerouslySetInnerHTML` with unvalidated data.
- Use React's built-in JSX escaping for all dynamic content.
- Add a `Content-Security-Policy` HTTP response header in production:
  - Disallow `unsafe-inline` scripts.
  - Restrict `connect-src` to the API gateway host.
  - Set `upgrade-insecure-requests`.
- Never attach tokens via URL query parameters.
- Store tokens only in memory (React state/context) or `sessionStorage`.
- Do not set `"secure": false` in `proxy.conf.json` or Vite proxy config
  in non-local environments.

---

## Docker Compose - Security Configuration

- Mount secrets into containers via read-only volumes or environment
  variables from a `.env` file that is NOT committed to git.
- All inter-service communication within the Compose network should use
  internal Docker networking. Only expose ports that need external access.
- Keycloak must be deployed with HTTPS enabled via `KC_HTTPS_*`
  environment variables in production.
- Pin every `FROM` directive to a specific version tag. Never use `:latest`.

---

## Keycloak - Authentication and Authorization

- Configure token lifetimes conservatively: access token max 5 minutes,
  refresh token max 30 minutes for internal sessions.
- Rotate client secrets when a secret is suspected to be exposed.
  Store client secrets exclusively in environment variables.

---

## Secrets and Credential Management

- Define all secrets as environment variables in the deployment pipeline.
- Never print environment variable values containing credentials in logs.
- In Python, load secrets via `pydantic-settings` `BaseSettings` classes.
  Validate that required settings are non-empty at startup.
- Rotate all long-lived credentials (passwords, client secrets, API keys)
  at least every 90 days.

---

## Dependency Vulnerability Scanning

- **Python**: run `pip audit` or `safety check` as part of the CI pipeline.
  Fix or document all high and critical findings.
- **Frontend**: run `npm audit --audit-level=high` as part of CI. Fix or
  document all high and critical findings.
- **Docker base images**: pin every `FROM` to a specific version tag.
  Scan images with Trivy before pushing to registry.

---

## Security Review Checklist

Before marking any security-related change as complete, confirm:

- [ ] No credentials, tokens, or key material appear in source code or
      configuration templates.
- [ ] All inputs at system boundaries are validated with Pydantic models
      or React form validation.
- [ ] No sensitive data is logged.
- [ ] Dependency vulnerability scan passes with no unmitigated
      high/critical findings.
- [ ] OAuth 2.0 tokens are validated by a proper JWT library.
- [ ] Docker images are pinned to a specific version.
- [ ] CORS is configured with explicit allowed origins.
- [ ] SQL queries use parameterized statements only.
