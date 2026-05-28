---
name: commit-preparation
description: >-
  Prepare a git commit for FinSight AI with safety checks: inspect staged
  changes, propose logical commit grouping, run a secret deny-list scan,
  and produce a commit message that follows
  `.github/git-commit-instructions.md`. Never executes `git commit`
  without an explicit `confirmed-terminal` approval. Keywords: commit,
  git commit, commit message, staged files, secret scan, pre-commit safety,
  prepare commit, conventional commit.
---

# Commit Preparation Skill

## Purpose

A safety-first wrapper around `git commit` for the FinSight AI repository. Performs local checks before any commit is executed.

This skill never runs `git commit`, `git commit --amend`, or `git push` without an explicit `confirmed-terminal` approval for the exact command shown.

---

## Step 1: Inspect Working Tree

Run, in order (with `confirmed-terminal` approval for each):

1. `git status --porcelain` - enumerate staged and unstaged changes.
2. `git diff --cached --stat` - summarise staged content.
3. `git diff --stat` - summarise unstaged content.

Refuse to proceed when:
- The working tree is clean (nothing to commit).
- The repository is in a rebase, merge, or cherry-pick state. Resolve first.

---

## Step 2: Secret and Forbidden-File Scan

For every staged path, refuse the commit when any staged file contains:

**Pattern matches (case-insensitive):**
- `sk-` (OpenAI key prefix)
- `OPENAI_API_KEY=` followed by a non-empty value
- `DATABASE_URL=` containing a password component
- Any `.env` file staged directly (warn the user; `.env` should be in `.gitignore`)
- Private key blocks: `-----BEGIN RSA PRIVATE KEY-----`, `-----BEGIN EC PRIVATE KEY-----`

If any match is found, report the file and line and refuse to proceed until the secret is removed.

---

## Step 3: Propose Commit Grouping

Inspect the staged diff and propose logical groupings:

- Group by module scope (backend agents, rag, api, frontend, infra, tests, docs).
- Suggest splitting into multiple commits if changes span unrelated scopes.
- Present the proposed grouping to the user for approval before writing the message.

---

## Step 4: Produce Commit Message

Follow `.github/git-commit-instructions.md`:

```
<type>(<scope>): <subject>

[optional body - explain WHY, not what; wrap at 72 chars]

[optional footer - Closes #N]
```

Valid types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`

Valid scopes: `backend`, `agents`, `rag`, `parsing`, `api`, `db`, `services`, `tools`, `telemetry`, `frontend`, `infra`, `docs`, `tests`

Rules:
- Subject: imperative mood, no period, max 72 chars.
- Never use the em dash; use a hyphen.
- Never use ampersand; write "and".

Present the proposed message to the user for approval before running `git commit`.

---

## Step 5: Execute with Confirmed-Terminal

Only after the user approves the message, present the final command for `confirmed-terminal` approval:

```
Command to run:
  git commit -m "<type>(<scope>): <subject>" -m "<body if any>"

Purpose:
  Commit staged changes with the approved commit message.

Risk: LOW
  Creates a local commit. Does not push to any remote.

Type YES to run, NO to skip.
```
