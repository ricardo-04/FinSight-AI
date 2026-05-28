---
name: azure-devops-pr
description: Prepare branch, commit, push, and PR steps for Azure DevOps
argument-hint: "<jira-issue> <user-story-id> <title> [target-branch]"
agent: General Purpose Agent
---

You prepare Azure DevOps pull request work for SalesMate.

## Input

- Jira issue: **${jira-issue}**
- User story ID: **${user-story-id}**
- Story title: **${title}**
- Target branch: **${target-branch}**
- Optional reviewers: **${reviewers}**
- Optional SSH key alias: **${ssh-key-alias}**
- Mode: **${mode}**

## Prerequisites

Azure CLI and the Azure DevOps extension must be installed and
authenticated before running Azure DevOps pull request commands. If they
are unavailable, produce manual pull request fields and browser fallback
steps instead.

## Defaults

- Target branch: `master`
- Organization: `https://dev.azure.com/cswsalesmate`
- Project: `SalesMate`
- Repository: `SalesMate`
- Reviewers:
  - `ra-pombo@criticalsoftware.com`
  - `pmfmonteiro@criticalsoftware.com`
  - `dsmendes@criticalsoftware.com`

## Workflow

1. Read `.github/constitution.md`, `.github/copilot-instructions.md`,
   `.github/git-commit-instructions.md`, and
   `.github/templates/PR_TEMPLATE.md`.
2. Validate the Jira issue, user story ID, story title, target branch,
   reviewer list, and mode.
3. Ask one focused question if any required input is missing.
4. Generate the branch name with this pattern:

   ```text
   feature/<JiraIssue>-<UserStoryId>-<Title-With-Proper-Casing>
   ```

5. Build the title segment from meaningful words in the story title.
   Strip bracket characters from screen references. Use `S4` instead of
   `[S4]`.
6. Generate the pull request title with this format:

   ```text
   <JiraIssue> <UserStoryId>: <Human readable title>
   ```

7. Generate a commit message that follows
   `.github/git-commit-instructions.md`.
8. Read the staged-file set before composing the final commit message.
9. Prepare the pull request body from
   `.github/templates/PR_TEMPLATE.md`.
10. Include validation evidence and mark missing checks as not configured
    or not run.
11. If command execution is requested, present the full command sequence,
    purpose, and risk level before running anything.
12. Do not run `git commit`, `git push`, `git merge`, `git rebase`,
    `git tag`, `git reset --hard`, `git push --force`, or
    `az repos pr create` unless the user explicitly requested that
    operation in the same message and approved the shown commands.

## Command Guidance

Use Azure CLI when it is available and authenticated:

```bash
az repos pr create \
  --organization "https://dev.azure.com/cswsalesmate" \
  --project "SalesMate" \
  --repository "SalesMate" \
  --source-branch "<branch-name>" \
  --target-branch "master" \
  --title "<pull-request-title>" \
  --description "<pull-request-body>" \
  --reviewers "ra-pombo@criticalsoftware.com" \
  --reviewers "pmfmonteiro@criticalsoftware.com" \
  --reviewers "dsmendes@criticalsoftware.com"
```

When the user asks to use `rsa_salesmate`, use this SSH wrapper for git
push commands:

```bash
GIT_SSH_COMMAND='ssh -i ~/.ssh/rsa_salesmate -o IdentitiesOnly=yes'
```

If Azure CLI is unavailable or authentication is blocked, produce the
manual pull request fields and the Azure DevOps repository pull request
page to open in a browser.

## Output

- Branch name.
- Commit message.
- Pull request title.
- Pull request body.
- Target branch.
- Reviewer list.
- Command plan, if execution was requested.
- Validation evidence and known limitations.

## Failure Handling

- On missing Jira or story data, ask for the missing values.
- On dirty or unexpected git state, stop and summarize the risk.
- On unavailable Azure CLI, provide browser fallback instructions.
- On authentication failure, stop and ask the user to sign in.