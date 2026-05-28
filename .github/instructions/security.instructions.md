---
applyTo: "**"
---

# Instructions - Security (OWASP)

## Overview

All code in FinSight AI must comply with the OWASP Top 10. These rules apply to both backend and frontend layers.

## A01 - Broken Access Control

- All API endpoints that return user-specific or document-specific data must verify the caller has permission to access that resource.
- Never rely on client-supplied IDs without server-side ownership validation.

## A02 - Cryptographic Failures

- Never store plaintext secrets; use environment variables loaded at runtime.
- Use HTTPS in production. The Docker Compose dev setup is HTTP only and must never be exposed publicly.
- Sensitive data at rest (document content, extracted metrics) should be stored in the database, not in logs or files.

## A03 - Injection

- Never build SQL queries by string concatenation with user input. Use SQLAlchemy ORM or parameterized queries.
- LLM prompts: sanitize user text before injection into prompts (see `ai-rag.instructions.md`).
- File uploads: validate MIME type and extension; never execute uploaded content.

## A04 - Insecure Design

- The extraction and RAG agents operate on user-uploaded PDFs. Assume PDFs may be malformed or malicious; catch and log parsing exceptions; never propagate raw parser errors to the API response.
- Limit file upload size via FastAPI's `UploadFile` and reject oversized files before processing.

## A05 - Security Misconfiguration

- CORS is restricted to `http://localhost:3000` in development. Production origins must be explicitly listed.
- Debug endpoints (if any) must be disabled in production via environment variable.
- Do not enable FastAPI's automatic OpenAPI UI (`/docs`, `/redoc`) in production without authentication.

## A06 - Vulnerable and Outdated Components

- Pin all dependency versions in `requirements.txt` and `package.json`.
- Review third-party library changelogs before upgrading major versions.

## A07 - Identification and Authentication Failures

- API keys (`OPENAI_API_KEY`, etc.) must never appear in logs, responses, or error messages.
- If authentication is added in the future, use short-lived tokens and validate on every request.

## A08 - Software and Data Integrity Failures

- Validate the structure and content of LLM responses before persisting them to the database.
- Do not execute or eval any LLM-generated code.

## A09 - Security Logging and Monitoring Failures

- Log all failed upload attempts (wrong MIME type, size exceeded) at WARNING level with document ID (not content).
- Log all agent errors at ERROR level with span trace ID for correlation.
- Never log the full request body; log only safe metadata (file name, size, document ID).

## A10 - Server-Side Request Forgery (SSRF)

- The `sec_fetch` tool makes outbound HTTP requests to SEC EDGAR. The target URL must be constructed from a validated base URL constant, never from raw user input.
- If the user can supply a URL (e.g., for document import), validate it against an allowlist of permitted hosts.
