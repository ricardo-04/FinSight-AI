# Git Commit Instructions

## Safety Rule

**Never run `git commit`, `git push`, or any other git write operation
(merge, rebase, tag, reset --hard, push --force, etc.) unless the user
explicitly requests it in that same message.**

All version control operations must be performed manually by the user after
reviewing and testing the changes. This rule applies globally to every agent,
task, and conversation, without exception.

## Branch Naming

Create branches using `scripts/new-branch.ps1` via the
`confirmed-terminal` skill. The script enforces the rules below.

### Supported branch types

| Type | When to use | JiraIssue | StoryId | Title | Version |
|---|---|---|---|---|---|
| `feature` | New functionality (default) | required | required | required | - |
| `bugfix` | Non-critical bug fixes | required | required | required | - |
| `hotfix` | Production emergency patches | required | optional | required | - |
| `docs` | Documentation updates | required | optional | required | - |
| `chore` | Dependency updates, config | required | optional | required | - |
| `refactor` | Code restructuring, no behaviour change | required | optional | required | - |
| `test` | Test suite additions or improvements | required | optional | required | - |
| `ci` | CI/CD pipeline changes | required | optional | required | - |
| `perf` | Performance optimisations | required | optional | required | - |
| `release` | Release preparation | - | - | - | required |

### Branch name formats

```
# feature and bugfix - StoryId is required
<type>/<JiraIssue>-<StoryId>-<Title-With-Proper-Casing>

# hotfix, docs, chore, refactor, test, ci, perf - StoryId is optional
<type>/<JiraIssue>-<Title-With-Proper-Casing>
<type>/<JiraIssue>-<StoryId>-<Title-With-Proper-Casing>

# release - version only
release/<Version>
```

### Rules

- `<JiraIssue>` uses the Jira issue key format `<PROJECT>-<NUMBER>`,
  for example `AIAPMMWP1-22`.
- `<StoryId>` uses the SalesMate story ID format `US-NNN`, for example
  `US-020`.
- The title uses meaningful words separated by hyphens in Proper-Case.
- Remove bracket characters from screen references. Use `S4` instead of
  `[S4]`.
- `release/` and `hotfix/` branches require an explicit `-BranchType`
  argument to the script - they are not reachable by accident.
- `master` is always protected and cannot be targeted by the script.

### Examples

```
feature/AIAPMMWP1-22-US-020-Document-Conversion-And-Rustfs-Integration-Supporting-S4
bugfix/AIAPMMWP1-45-US-031-Fix-Login-Timeout
hotfix/AIAPMMWP1-99-Critical-Auth-Bypass
docs/AIAPMMWP1-50-Api-Reference-Update
chore/AIAPMMWP1-60-Upgrade-Node-Lts
release/1.2.0
release/1.2.0-rc1
```

## Pull Request Defaults

Use these Azure DevOps defaults unless the user gives a different value:

- Target branch: `master`
- Organization: `https://dev.azure.com/cswsalesmate`
- Project: `SalesMate`
- Repository: `SalesMate`
- Reviewers:
	- `ra-pombo@criticalsoftware.com`
	- `pmfmonteiro@criticalsoftware.com`
	- `dsmendes@criticalsoftware.com`
    - `caferreira@criticalsoftware.com`

Pull request titles use this format:

```
<JiraIssue> <UserStoryId>: <Human readable title>
```

Example:

```
AIAPMMWP1-22 US-020: Document conversion and RustFS integration supporting S4
```

## Commit Message Format

When the user explicitly requests a commit, use the following format:

```
<story/task ID>: <story/task description>

* <simple resume of a change>
* <simple description of another change>
```

Rules:
- The first line is `<ID>: <description>` with no trailing punctuation.
- Leave exactly one blank line between the first line and the bullet list.
- Each bullet uses a `*` prefix followed by a single space.
- Each bullet is a concise single sentence; no sub-bullets.
- No full stops at the end of bullet lines.
- Do not add a sign-off, co-author, or extra metadata unless explicitly asked.

## Examples

Single-change commit:

```
AIAPMMWP1-22: Update deployment to include backend services

* Update default VM IP
```

Multi-change commit:

```
AIAPMMWP1-22: Update deployment to include backend services

* Update deployment to include backend services
* Update default docker image of frontend
* Fix download of config file
```

## Staged Files

Before composing the commit message, show the user the list of files that
will be included (`git status --short` or `git diff --cached --name-only`)
and wait for confirmation that the staged set is correct.
