---
name: dependency-upgrade
description: Plan and validate safe backend or frontend dependency upgrades
argument-hint: "<backend-or-frontend-and-packages>"
agent: general-purpose
---

You are planning a dependency upgrade for SalesMate.

## Input

- Target module and packages: **${backend-or-frontend-and-packages}**

## Workflow

1. Read `.github/skills/dependency-update/SKILL.md`.
2. Inventory current package versions and lock files.
3. Identify security advisories, breaking changes, and migration notes.
4. Ask for approval before changing dependency manifests or lock files.
5. Run build, tests, and audits after command approval.

## Output

- Upgrade plan.
- Risk summary.
- Files expected to change.
- Validation commands and results.