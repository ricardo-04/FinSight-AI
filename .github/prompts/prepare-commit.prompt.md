---
name: prepare-commit
description: Prepare a single git commit using the commit-preparation skill
argument-hint: "[story-or-task-id] [optional commit grouping hint]"
agent: General Purpose Agent
skills: [confirmed-terminal, commit-preparation]
---

You prepare a single git commit for the SalesMate repository.

## Input

- Story or task ID: **${story-or-task-id}**
- Optional grouping hint: **${grouping-hint}**

## Workflow

1. Load the `commit-preparation` skill at
   `.github/skills/commit-preparation/SKILL.md` and follow its six
   steps in order.
2. If the story or task ID was not provided, attempt to parse it
   from the current branch name using the pattern
   `feature/<JiraIssue>-<UserStoryId>-<Title-With-Proper-Casing>`
   defined in `.github/git-commit-instructions.md`. If parsing
   fails, ask the user once.
3. Print the staged file list, the proposed commit message, and the
   risk classification before requesting approval.
4. Run `git commit` only after a `confirmed-terminal` approval for
   the exact command shown.

## Output

- Staged file list.
- Proposed commit message.
- Pre-commit check results (secret scan, test evidence verdict).
- Final commit hash and short status, on success.
- A clear refusal message naming the failed precondition, on
  refusal.

## Refusals

- Never run `git commit --no-verify`.
- Never amend or squash existing commits unless the user requests
  it in the same message.
- Never run `git push`. Push is a separate prompt and requires its
  own approval.
