---
applyTo: "docs/**,README.md,.github/**/*.md"
---

# Instructions - Documentation

## Scope

These rules apply to project documentation, repository governance files,
Copilot customization files, templates, prompts, skills, personas, and
agent descriptions.

## Documentation Rules

- Write all documentation in English.
- Keep prose near 72 characters per line.
- Use concise headings and short paragraphs.
- Use Markdown tables for inventories, decisions, and checklists.
- Use `docs/architecture/decisions/` for Architecture Decision Records.
- Link to existing files with workspace-relative paths.
- Keep status language explicit: planned, implemented, deferred, or not
  configured.
- Do not state that a command, workflow, test runner, linter, or service
  exists unless it is present in the repository.

## Validation Rules

- Cross-check claims against source files before documenting them.
- Mark external systems as unverified when authenticated access is not
  available.
- Record deferred items as follow-up work instead of presenting them as
  complete.