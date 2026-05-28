---
name: azure-devops-commit
description: Prepare Azure DevOps commit and pull request commands
argument-hint: "<jira-issue> <user-story-id> <title> [actor-email]"
agent: General Purpose Agent
---

You prepare Azure DevOps commit work for SalesMate.

## Input

- Jira issue: **${jira-issue}**
- User story ID: **${user-story-id}**
- Story title: **${title}**
- Actor email: **${actor-email}**
- Target branch: **${target-branch}**
- Optional reviewers: **${reviewers}**
- Optional SSH key alias: **${ssh-key-alias}**
- Mode: **${mode}**

## Prerequisites

Azure CLI and the Azure DevOps extension must be installed and
authenticated before running Azure DevOps pull request commands. If they
are unavailable, produce manual pull request fields and browser fallback
steps instead.

## Source Rules

Read these files before producing output:

- `.github/constitution.md`
- `.github/copilot-instructions.md`
- `.github/git-commit-instructions.md`
- `.github/templates/PR_TEMPLATE.md`

## Reviewer Exclusion Rule

The pull request creator must not be included in the final reviewer list.

Apply this rule every time:

1. Start from the reviewers supplied by the user, or from the default
   reviewers in `.github/git-commit-instructions.md`.
2. Resolve the actor email from explicit input when available.
3. If command execution is requested and actor email is missing, propose
   reading it from `git config user.email` or Azure CLI identity after
   user approval.
4. Normalize the actor email and reviewer emails case-insensitively.
5. Remove the actor email from the final reviewer list.
6. Never pass the actor email to `az repos pr create --reviewers`.
7. If no reviewers remain, omit reviewer flags and report why.

Example:

```text
Actor: caferreira@criticalsoftware.com
Default reviewers: ra-pombo@criticalsoftware.com,
pmfmonteiro@criticalsoftware.com, dsmendes@criticalsoftware.com,
caferreira@criticalsoftware.com
Final reviewers: ra-pombo@criticalsoftware.com,
pmfmonteiro@criticalsoftware.com, dsmendes@criticalsoftware.com
```

## Workflow

1. Validate the Jira issue, user story ID, story title, target branch,
   actor email, reviewer list, SSH key alias, and mode.
2. Ask one focused question if required input is missing.
3. Generate the branch name with this pattern:

   ```text
   feature/<JiraIssue>-<UserStoryId>-<Title-With-Proper-Casing>
   ```

4. Strip bracket characters from screen references. Use `S4` instead of
   `[S4]`.
5. Read the staged-file set before composing the final commit message.
6. Generate the commit message following
   `.github/git-commit-instructions.md`.
7. Generate the pull request title with this format:

   ```text
   <JiraIssue> <UserStoryId>: <Human readable title>
   ```

8. Build the pull request body from `.github/templates/PR_TEMPLATE.md`.
9. Apply the reviewer exclusion rule before writing reviewer output or
   command examples.
10. Include validation evidence and mark missing checks as not configured
    or not run.
11. If command execution is requested, present the command sequence,
    purpose, and risk level before running anything.
12. Do not run `git commit`, `git push`, `git merge`, `git rebase`,
    `git tag`, `git reset --hard`, `git push --force`, or
    `az repos pr create` unless the user explicitly requested that
    operation in the same message and approved the shown commands.

## Command Guidance

Use the configured Azure DevOps defaults from
`.github/git-commit-instructions.md` unless the user overrides them.

When the user asks to use `rsa_salesmate`, use this SSH wrapper for git
push commands:

```bash
GIT_SSH_COMMAND='ssh -i ~/.ssh/rsa_salesmate -o IdentitiesOnly=yes'
```

When creating the pull request with Azure CLI, include only the filtered
reviewers:

```bash
az repos pr create \
  --organization "https://dev.azure.com/cswsalesmate" \
  --project "SalesMate" \
  --repository "SalesMate" \
  --source-branch "<branch-name>" \
  --target-branch "master" \
  --title "<pull-request-title>" \
  --description "<pull-request-body>" \
  --reviewers "<filtered-reviewer-1>" \
  --reviewers "<filtered-reviewer-2>"
```

If Azure CLI is unavailable or authentication is blocked, produce the
manual pull request fields and browser fallback steps.

## Output

- Branch name.
- Actor email source.
- Commit message.
- Pull request title.
- Pull request body.
- Target branch.
- Final reviewer list after actor exclusion.
- Command plan, if execution was requested.
- Validation evidence and known limitations.

## Failure Handling

- On missing Jira or story data, ask for the missing values.
- On missing actor email, ask for it before creating PR reviewer output.
- On dirty or unexpected git state, stop and summarize the risk.
- On unavailable Azure CLI, provide browser fallback instructions.
- On authentication failure, stop and ask the user to sign in.