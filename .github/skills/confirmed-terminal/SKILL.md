---
name: confirmed-terminal
description: >-
  Enforces a user-confirmation gate before every shell command executed
  with a terminal execution tool. Use this skill whenever a task requires
  running a terminal command: build scripts, docker compose, openssl, uv, npm,
  Bash scripts, or any other shell invocation. Keywords: run command,
  execute shell, terminal, bash, docker, uv, npm, openssl, script,
  confirmed-terminal, user approval, command confirmation.
---

# Confirmed Terminal Skill

## Purpose

No shell command may run without the user's explicit approval. This skill
defines the mandatory confirmation gate that every agent must apply before
invoking a terminal execution tool.

---

## Risk Classification

Classify every command before presenting it to the user:

| Risk level | Examples |
|---|---|
| LOW | `ls`, `cat`, `docker ps`, `uv run pytest`, `npm run build`, `echo` |
| MEDIUM | `docker compose up`, `docker compose restart`, file writes, |
| | `uv sync --group dev`, `npm install` |
| HIGH | `rm`, `docker compose down -v`, database drop, `reset` of |
| | any data store, overwriting certificates or keystores |

---

## Step 1: Present the Command for Approval

Before calling a terminal execution tool, output a confirmation block using
this exact format:

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

## Step 2: Interpret the User Response

| User says | Agent action |
|---|---|
| `yes`, `y`, `run`, `go`, `confirm`, `ok`, `proceed`, `approve` | Execute the command |
| `no`, `n`, `skip`, `cancel`, `abort` | Skip the command; continue with remaining work |
| A different command | Present that command through Step 1 again before running |
| Any other response | Ask for clarification; do not execute |

The match is case-insensitive and trims leading and trailing whitespace.

---

## Step 3: Execute and Report

After receiving approval, run the command and report:

```
Running: <command>

Output:
<actual command output>

Result: SUCCESS | FAILED (exit code <N>)
```

If the command fails:
1. Show the full error output.
2. Propose a corrective command and go back to Step 1.
3. Do not retry silently or with a modified command without re-confirming.

---

## Step 4: Handle Sequences of Commands

When a task requires multiple commands:
1. Present ALL commands at once, numbered, with risk level and purpose for
   each.
2. Ask the user to approve the full sequence or select which to run.
3. Run approved commands in order; stop and report if any command fails.

Example:
```
Commands to run:

  1. [MEDIUM] mkdir -p deployment-tests/certs
     Creates the target certificate directory.

  2. [MEDIUM] bash tools/api-gateway/scripts/generate-dev-certs.sh \
       deployment-tests/certs 10.110.6.13
     Generates the CA and all service certificates.

Type YES to run all, or list the numbers to run (e.g. "1 2").
```

---

## Rules

- NEVER call a terminal tool before receiving explicit approval for THAT command.
- NEVER silently retry a failed command with modified arguments.
- NEVER batch commands inside a single `execute` call without presenting
  all of them in Step 1 first.
- ALWAYS show the actual command output after execution, even on success.
- ALWAYS classify risk conservatively; when in doubt, use the higher level.
