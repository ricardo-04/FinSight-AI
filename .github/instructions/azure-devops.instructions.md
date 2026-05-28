---
applyTo: "**"
---

# Instructions - Azure DevOps

## Scope

These rules apply to every interaction with Azure DevOps from this
repository: the Azure CLI (`az`), the `az repos` extension,
`az rest` calls, and the SalesMate organisation, project, and
repository.

These rules complement, and never override,
`.github/constitution.md`,
`.github/git-commit-instructions.md`, and
`.github/instructions/git-workflow.instructions.md`.

---

## Defaults

| Field | Value |
|---|---|
| Organisation | `https://dev.azure.com/cswsalesmate` |
| Project | `SalesMate` |
| Repository | `SalesMate` |
| Default target branch | `master` |
| Default reviewers | See `.github/git-commit-instructions.md` |

Always read defaults from `.github/git-commit-instructions.md`.
Never hard-code reviewer email addresses in agent or skill output.

---

## Authentication

- Run `az login` once per machine. The Azure DevOps extension is
  installed with `az extension add --name azure-devops`.
- Configure defaults once with:

  ```bash
  az devops configure --defaults \
    organization=https://dev.azure.com/cswsalesmate \
    project=SalesMate
  ```

- Every Azure DevOps skill must call `az account show` first. If
  the call fails, fall back to printing manual instructions and a
  browser URL. Do not silently skip remote actions.

---

## Allowed CLI Surface

| Surface | Purpose | Used by |
|---|---|---|
| `az account show` | Identify the actor UPN | All Azure DevOps skills |
| `az repos pr list` | Discover pull requests | Pull Request Reviewer |
| `az repos pr show` | Read pull request metadata | Pull Request Reviewer |
| `az repos pr create` | Create a pull request | Pull Request Create skill |
| `az repos pr set-vote` | Cast a vote on a pull request | Pull Request Reviewer (vote step only) |
| `az rest --method GET /threads` | Read existing comment threads | Pull Request Reviewer |
| `az rest --method POST /threads` | Post a new comment thread | Pull Request Reviewer (per-comment approval) |

---

## Forbidden CLI Surface

The following calls are forbidden in agent and skill output. They
must be refused even when the signed-in identity holds the
permission required to execute them.

- `az repos pr update --auto-complete` (any value).
- `az repos pr complete`.
- `az repos pr set-vote --vote reset` against a vote not cast by
  the actor in the current session.
- `az repos pr policy ...` (modifies branch policies).
- `az repos pr create --bypass-policy` and
  `--bypass-policy-reason`.
- `az rest --method PATCH .../threads/<id>` for threads where
  `author.uniqueName != actor UPN`.
- `az rest --method POST .../threads/<id>/comments` for threads
  where `author.uniqueName != actor UPN`.
- `az repos ref delete` (deletes a branch).
- `az devops security permission ...` (changes permissions).

---

## Comment Authorship

Every comment posted by an agent or skill must be prefixed with:

```text
[AI-assisted review by <UPN>]
```

The `<UPN>` value comes from
`az account show --query user.name -o tsv`. Reviewers rely on the
prefix to distinguish AI-drafted comments from human-authored
comments. The prefix is mandatory; agents must refuse to post a
comment without it.

---

## Reviewer Exclusion

Apply the actor-exclusion rule from
`.github/prompts/azure-devops-commit.prompt.md` every time
reviewers are passed to `az repos pr create`. Normalise emails
case-insensitively. Never include the actor in the final reviewer
list. When the resulting list is empty, omit `--reviewers` and
report why.

---

## Vote Confirmation

`az repos pr set-vote` runs only after a separate, distinct user
turn (not the same turn as any comment-posting approval) in which
the user types the vote value back. Default to `wait-for-author`
when the test-evidence file for the source branch is missing or
did not pass, or when any comment posted in the current session
was marked blocking by the user.

---

## Fallback When Azure CLI Is Unavailable

When `az account show` fails, agents and skills must:

1. Print the manual fields the user needs to fill (title,
   description, source, target, reviewers).
2. Print the Azure DevOps browser URL for the source branch:

   ```text
   https://dev.azure.com/cswsalesmate/SalesMate/_git/SalesMate/pullrequestcreate?sourceRef=<branch>&targetRef=master
   ```

3. Stop. Do not retry the CLI call without an explicit user
   request.
