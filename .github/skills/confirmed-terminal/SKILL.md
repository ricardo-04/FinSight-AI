---
name: confirmed-terminal
description: >-
  Enforces a user-confirmation gate before every shell command executed
  with a terminal execution tool. Use this skill whenever a task requires
  running a terminal command: pytest, uvicorn, docker compose, pip install,
  npm install, npm run build, npm run test, or any other shell invocation.
  Keywords: run command, execute shell, terminal, docker, pip, npm, pytest,
  uvicorn, script, confirmed-terminal, user approval, command confirmation.
---

# Confirmed Terminal Skill

## Purpose

No shell command may run without the user's explicit approval. This skill defines the mandatory confirmation gate every agent must apply before invoking any terminal execution tool.

---

## Risk Classification

Classify every command before presenting it to the user:

| Risk level | Examples |
|---|---|
| LOW | `pytest`, `npm run test`, `npm run build`, `uvicorn` (dev), `docker ps`, `git status` |
| MEDIUM | `docker compose up`, `docker compose restart`, `pip install`, `npm install`, file writes, `uv sync` |
| HIGH | `docker compose down -v`, database reset, `rm -rf`, overwriting `.env`, dropping tables |

---

## Step 1: Present the Command for Approval

Before calling any terminal execution tool, output a confirmation block using this exact format:

```
Command to run:
  <command>

Purpose:
  <one-sentence explanation of why this command is needed>

Risk: <LOW | MEDIUM | HIGH>
  <brief description of what will change or be affected>

Type YES to run, NO to skip, or provide an alternative command.
```

For HIGH-risk commands, prefix the block with:
```
WARNING: this command is destructive and may be difficult to reverse.
```

---

## Step 2: Await Response

- If the user types YES (any case): execute the command exactly as shown.
- If the user types NO: skip the command and report it as skipped.
- If the user provides an alternative: show a new confirmation block for the alternative.
- Never assume approval. Never run the command before receiving YES.

---

## Step 3: Report Output

After execution, report:
- Exit code.
- Relevant output (last 20-30 lines for long outputs).
- Any errors encountered and a proposed fix.
