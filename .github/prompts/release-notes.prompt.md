---
name: release-notes
description: Generate concise release notes from changes and validation evidence
argument-hint: "<change-range-or-summary>"
agent: general-purpose
---

You are preparing release notes for SalesMate.

## Input

- Change range or summary: **${change-range-or-summary}**

## Workflow

1. Identify user-facing changes, technical changes, migrations, and
   operational notes.
2. Group changes by backend, frontend, infrastructure, documentation, and
   security.
3. Include validation evidence and known limitations.
4. Exclude internal chat details and sensitive information.

## Output

- Summary.
- Added, changed, fixed, and security sections.
- Validation evidence.
- Known limitations and follow-up work.