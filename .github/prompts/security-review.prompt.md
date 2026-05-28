---
name: security-review
description: Review SalesMate changes for security risks and compliance gaps
argument-hint: "<scope-or-files>"
agent: story-qa-review
---

You are performing a security review for SalesMate.

## Input

- Scope or files: **${scope-or-files}**

## Workflow

1. Read `.github/instructions/security.instructions.md`.
2. Identify authentication, authorization, input validation, storage,
   network, dependency, and logging changes.
3. Check for hardcoded secrets, token leakage, unsafe CORS, SQL injection,
   missing JWT validation, and insecure Docker settings.
4. Verify tests or validation evidence for security-sensitive behavior.

## Output

- Severity-ordered findings.
- Evidence from repository files.
- Required fix for each finding.
- Security checks that passed.

Do not edit files unless the user explicitly asks for remediation.