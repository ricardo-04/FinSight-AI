---
name: code-review
description: Perform a risk-focused code review for changed files
argument-hint: "<change-summary-or-files>"
agent: story-qa-review
---

You are performing a risk-focused code review for SalesMate.

## Input

- Change summary or files: **${change-summary-or-files}**

## Workflow

1. Identify changed files and affected modules.
2. Read `.github/copilot-instructions.md` and relevant path-specific
   instructions.
3. Review correctness, security, tests, backwards compatibility, and
   documentation.
4. Lead with findings ordered by severity.
5. Include file references and actionable corrections.

## Output

- Findings first.
- Open questions or assumptions.
- Brief validation summary.
- Residual risk if no findings are present.

Do not edit files unless the user explicitly asks for fixes.