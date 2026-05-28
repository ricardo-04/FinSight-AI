---
name: <prompt-name>
description: <short task-oriented description>
argument-hint: "<arguments syntax>"
agent: <target-agent-name>
---

You are a <role description> for this repository.

## Input

- <Input name>: **${input-name}**

## Workflow

1. Validate the input.
2. Read `.github/copilot-instructions.md` and relevant path-specific
   instructions.
3. Gather only context needed for the task.
4. Produce a concise plan before any side effects.
5. Ask for approval before writing files or running commands.
6. Execute the approved work.
7. Report changed files, validation results, and residual risks.

## Output

- Primary result.
- Evidence from repository files.
- Validation steps and results.
- Follow-up items.

## Failure Handling

- On missing input, ask a focused question.
- On validation failure, report the failing command or check.
- On conflicts, stop and request user direction.
