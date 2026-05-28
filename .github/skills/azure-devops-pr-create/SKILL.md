---
name: azure-devops-pr-create
description: >-
  Create a pull request on Azure DevOps for SalesMate using the project
  conventions in `.github/git-commit-instructions.md` and the template at
  `.github/templates/PR_TEMPLATE.md`. Wraps `az repos pr create`. Auto-marks
  the PR as draft when the test-evidence artifact for the source branch is
  missing. Reuses `confirmed-terminal` for the remote write. Keywords:
  pull request, az repos pr create, Azure DevOps, draft PR, reviewer
  exclusion, test evidence.
---

# Azure DevOps Pull Request Create Skill

## Purpose

Produce and create a single pull request on Azure DevOps with safe
defaults, deterministic title and description, the project's reviewer
exclusion rule, and a draft fallback when test evidence is missing.

This skill never runs `az repos pr create` without an explicit
`confirmed-terminal` approval for the exact command shown.

---

## Inputs

- Source branch (default: current branch from
  `git rev-parse --abbrev-ref HEAD`).
- Target branch (default: `master`).
- Story id and Jira issue id (parsed from the branch name).
- Story title (asked from the user if not parseable from the branch).
- Actor email (read from `git config user.email` or `az account show`).
- Optional reviewer overrides.

---

## Defaults

Read from `.github/git-commit-instructions.md`:

- Organisation: `https://dev.azure.com/cswsalesmate`
- Project: `SalesMate`
- Repository: `SalesMate`
- Default reviewers:
  - `ra-pombo@criticalsoftware.com`
  - `pmfmonteiro@criticalsoftware.com`
  - `dsmendes@criticalsoftware.com`
  - `caferreira@criticalsoftware.com`

---

## Step 1: Preconditions

Refuse to proceed when any of the following holds:

1. `az` CLI is not installed or `az account show` fails. Fall back
   to printing the manual PR fields and the Azure DevOps browser URL
   for the source branch.
2. The source branch has not been pushed to `origin`
   (`git ls-remote --heads origin <branch>` returns empty).
3. A pull request already exists for the source branch (detected via
   `az repos pr list --source-branch <branch>`).

---

## Step 2: Title and Description

Build the title:

```text
<JiraIssue> <UserStoryId>: <Human readable title>
```

Build the description from `.github/templates/PR_TEMPLATE.md`. Fill
the standard sections from:

- Commit messages on the source branch
  (`git log --pretty=format:'* %s' <target>..<source>`).
- The story acceptance criteria from
  `docs/user-stories.csv` if the story id is found.
- The test-evidence file at
  `.github/copilot-outputs/<branch>-*-test-evidence.md`.

When a section cannot be filled from evidence, write `Not configured`
or `Not run` rather than fabricating content.

---

## Step 3: Reviewer List

Apply the actor-exclusion rule from
`.github/prompts/azure-devops-commit.prompt.md`:

1. Start from default reviewers.
2. Normalise emails case-insensitively.
3. Remove the actor email.
4. If no reviewers remain, omit the `--reviewers` flag and note the
   reason in the output.

---

## Step 4: Draft Decision

If the test-evidence file is missing, or its verdict is not
`Result: PASS`, the PR is created as draft. The skill must add this
sentence at the top of the description:

```text
Draft: test evidence is missing or did not pass. Mark this PR ready
only after a passing test-evidence artifact exists.
```

---

## Step 5: Approval and Execution

Print the full proposal:

```text
Source branch:    <branch>
Target branch:    <target>
Title:            <title>
Description:      <multi-line>
Reviewers:        <list, after exclusion>
Linked work item: <id>
Draft:            <YES | NO>

Command to run:
  az repos pr create \
    --organization "https://dev.azure.com/cswsalesmate" \
    --project "SalesMate" \
    --repository "SalesMate" \
    --source-branch "<branch>" \
    --target-branch "<target>" \
    --title "<title>" \
    --description "<description>" \
    [--draft] \
    [--reviewers "<email>" ...]

Risk: MEDIUM
  Creates a remote pull request. Reversible by abandoning the PR
  in Azure DevOps.

Type YES to run.
```

Run the command only after a `confirmed-terminal` approval.

---

## Refusals

- Never auto-complete the PR.
- Never set merge options.
- Never assign reviewers outside the default list plus
  `.github/CODEOWNERS` routing, and always exclude the actor.
- Never use `--bypass-policy` or `--bypass-policy-reason`.
- Never push the source branch from this skill; push is a separate,
  separately gated action.
