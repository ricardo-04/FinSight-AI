---
name: generate-tests
description: Generate focused backend or frontend tests for changed behavior
argument-hint: "<module-or-files-and-behavior>"
agent: story-orchestrator
---

You are generating tests for SalesMate behavior.

## Input

- Module, files, and behavior: **${module-or-files-and-behavior}**

## Workflow

1. Identify the module and relevant instruction files.
2. Read existing code and nearby tests.
3. Plan test cases for happy paths, errors, edge cases, and security
   behavior.
4. Ask for confirmation before adding dependencies.
5. Add tests using the tooling already configured in the project files.
6. If required tooling is missing, produce a setup plan and ask for
   explicit approval before changing project files or dependencies.
7. Run the available test command after user approval.

## Output

- Tests added.
- Behavior covered.
- Commands run and results.
- Remaining coverage gaps.