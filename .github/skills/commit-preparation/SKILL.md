---
name: commit-preparation
description: >-
  Prepare a single git commit for SalesMate with safety checks: inspect
  staged and unstaged changes, propose logical commit grouping, run a
  secret deny-list scan, verify the test-evidence artifact exists, and
  produce a commit message that follows
  `.github/git-commit-instructions.md`. Never executes `git commit`
  without an explicit `confirmed-terminal` approval. Keywords: commit,
  git commit, commit message, staged files, secret scan, test evidence,
  pre-commit safety.
---

# Commit Preparation Skill

## Purpose

Provide a deterministic, safety-first wrapper around `git commit` for
the SalesMate repository. This skill compensates for the absence of a
CI pipeline and pre-commit hooks by performing local checks before any
commit is executed.

This skill never runs `git commit`, `git commit --amend`,
`git commit --no-verify`, `git push`, or any rewrite operation
without an explicit `confirmed-terminal` approval for the exact
command shown.

---

## Inputs

- Current branch name (read from `git rev-parse --abbrev-ref HEAD`).
- Story or task ID (parsed from the branch name when it follows
  `feature/<JiraIssue>-<UserStoryId>-<Title>`, otherwise asked from
  the user).
- Optional: user-provided list of intended logical commit groups.

---

## Step 1: Inspect Working Tree

Run, in order:

1. `git status --porcelain` to enumerate staged and unstaged changes.
2. `git diff --cached --stat` to summarise staged content.
3. `git diff --stat` to summarise unstaged content.

Refuse to proceed when:

- The working tree is clean (nothing to commit).
- The repository is in a rebase, merge, or cherry-pick state
  (`.git/REBASE_HEAD`, `.git/MERGE_HEAD`, or `.git/CHERRY_PICK_HEAD`
  exist). The user must resolve the in-progress operation first.

---

## Step 2: Secret and Forbidden-File Deny List

For every staged path, refuse the commit when any path matches:

- `.env`, `.env.*`
- `*.pem`, `*.key`, `*.pfx`, `*.crt`, `*.p12`
- `id_rsa*`, `id_ed25519*`
- Any path under `infra/nginx/certs/`
- Any path under `secrets/` or `private/`
- Any file larger than 5 MB (likely an artifact or binary blob)

Additionally scan the staged diff for these substrings (case
insensitive):

- `BEGIN RSA PRIVATE KEY`
- `BEGIN OPENSSH PRIVATE KEY`
- `aws_secret_access_key`
- `client_secret`
- `xoxb-`, `xoxp-` (Slack tokens)

On any match, stop and report the matching path or line range. The
user must remove the file from the index (`git restore --staged`)
before this skill proceeds.

---

## Step 3: Verify Test Evidence

Look for a sibling test-evidence file under
`.github/copilot-outputs/<branch>-*-test-evidence.md`.

- If the file exists and contains the literal verdict line `Result:
  PASS`, continue.
- If the file is missing or its verdict is not `PASS`, warn the user
  and require explicit acknowledgement (the user types
  `acknowledge missing tests`) before proceeding. This is the
  no-CI substitute for a build-validation status check.

---

## Step 4: Propose Commit Grouping

When the staged set spans more than one logical concern, propose a
grouping plan as numbered bundles with file lists. Wait for the user
to choose one of:

- Accept the proposed grouping and stage one bundle at a time.
- Provide an alternative grouping.
- Commit everything as a single commit.

Do not stage or unstage files automatically without approval.

---

## Step 5: Compose Commit Message

Follow `.github/git-commit-instructions.md` exactly:

```text
<story-or-task-id>: <human-readable description>

* <change summary>
* <change summary>
```

Rules enforced:

- First line `<ID>: <description>`, no trailing punctuation.
- Exactly one blank line before the bullet list.
- Each bullet starts with `* ` and a single concise sentence.
- No sub-bullets, no full stops at end of bullet lines.
- No sign-off, co-author, or extra metadata unless the user asked
  for it in the same turn.

---

## Step 6: Approval and Execution

Print:

```text
Staged files:
  <list>

Commit message:
  <message>

Risk: MEDIUM
  Local commit. Reversible only with `git reset --soft HEAD~1`
  before push.

Type YES to run `git commit -F <temp-message-file>`.
```

Run the commit only after the user types an approval matching the
`confirmed-terminal` rules. Push is a separate, separately gated
action and is not part of this skill.

---

## Refusals

- Never amend or squash existing commits unless the user requests
  it in the same turn.
- Never run `git commit --no-verify`.
- Never silently retry after a failure.
- Never commit when secret or forbidden-file checks fail.
