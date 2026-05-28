---
name: azure-devops-pr-review
description: >-
  Discover pull requests assigned to the signed-in Azure DevOps identity,
  read their metadata, diffs, and existing threads, produce a structured
  findings file under `.github/copilot-outputs/`, post comment threads
  one at a time under explicit human approval, and cast a vote in a
  separate, explicitly approved user turn. Keywords: PR review, pull
  request review, Azure DevOps reviewer, az rest threads, set-vote,
  AI-assisted review.
---

# Azure DevOps Pull Request Review Skill

## Purpose

Provide the bounded read-and-write surface used by the Pull Request
Reviewer Agent. The skill is the only place in the project where
remote Azure DevOps writes other than `az repos pr create` are
permitted.

The skill obeys ADR-0001 at
`docs/architecture/decisions/ADR-0001-pull-request-reviewer-agent.md`
and the seven hard guardrails defined there.

---

## Read-Only Surface (steps 1 to 5)

These steps run without requiring `confirmed-terminal` because they
have no remote side effects.

1. Identify the actor:

   ```bash
   az account show --query user.name -o tsv
   ```

2. List assigned pull requests:

   ```bash
   az repos pr list \
     --organization "https://dev.azure.com/cswsalesmate" \
     --project "SalesMate" \
     --repository "SalesMate" \
     --reviewer "@me" \
     --status active
   ```

3. For each PR id, read metadata, linked work items, and existing
   comment threads:

   ```bash
   az repos pr show --id <prId>
   az rest --method GET --uri \
     "https://dev.azure.com/cswsalesmate/SalesMate/_apis/git/repositories/SalesMate/pullRequests/<prId>/threads?api-version=7.1"
   ```

4. Compute the local diff:

   ```bash
   git fetch origin <target> <source>
   git diff origin/<target>...origin/<source>
   ```

5. Write a findings file at
   `.github/copilot-outputs/<branch>-pr-review-output.md` using the
   sections in
   `.github/prompts/code-review.prompt.md`. Always include:

   - PR id, title, author, source branch, target branch.
   - Linked work item and acceptance-criteria mapping when the
     story id can be parsed from the branch name. Supported
     patterns:
     - `<type>/<JiraIssue>-<StoryId>-<Title>` where `<type>` is
       one of `feature`, `bugfix`, `hotfix`, `docs`, `chore`,
       `refactor`, `test`, `ci`, `perf`.
     - `<type>/<JiraIssue>-<Title>` (StoryId absent).
     - `release/<Version>`.
   - Risk-ranked findings.
   - Proposed comments (numbered) with file path and line range
     when inline.
   - Proposed vote with the literal value
     (`approve`, `approve-with-suggestions`, `wait-for-author`, or
     `reject`) and the reason.
   - An empty `Session log` section that will be appended to in
     steps 6 and 7.

---

## Write Surface (steps 6 and 7)

### Step 6: Post a Single Comment

For each proposed comment, present:

```text
Pull request:  <id>
Target file:   <path or "PR-level">
Line range:    <start..end or "n/a">
Thread status: active
Body:
  [AI-assisted review by <UPN>]
  <comment text>

Risk: MEDIUM
  Posts a remote comment thread under your identity.

Type YES to post this comment.
```

On approval, run:

```bash
az rest --method POST \
  --uri "https://dev.azure.com/cswsalesmate/SalesMate/_apis/git/repositories/SalesMate/pullRequests/<prId>/threads?api-version=7.1" \
  --body @<thread-body.json>
```

**PR-level comment** - `thread-body.json` structure:

```json
{
  "comments": [
    {
      "parentCommentId": 0,
      "content": "[AI-assisted review by <UPN>]\n<comment text>",
      "commentType": 1
    }
  ],
  "status": 1
}
```

**Inline file comment** - `thread-body.json` structure (anchored to a
specific file and line):

```json
{
  "comments": [
    {
      "parentCommentId": 0,
      "content": "[AI-assisted review by <UPN>]\n<comment text>",
      "commentType": 1
    }
  ],
  "status": 1,
  "threadContext": {
    "filePath": "/<repo-relative-file-path>",
    "rightFileStart": { "line": <start-line>, "offset": 1 },
    "rightFileEnd":   { "line": <end-line>,   "offset": 1 }
  }
}
```

Use `rightFileStart`/`rightFileEnd` for lines added in the PR diff
(right side). Use `leftFileStart`/`leftFileEnd` for lines removed
(left side). Set `"offset": 1` when no character-level precision
is needed.

Append the returned thread id to the findings file `Session log`.

Refusals enforced in this step:

- Never batch approvals. One `az rest POST` per user approval.
- Never set `status` to anything other than `active` on creation.
- Never call `PATCH .../threads/<id>` or `POST .../threads/<id>/comments`
  for threads where `author.uniqueName != actor UPN`.

### Step 7: Cast a Vote

The vote step requires a separate, distinct user turn from any
comment-posting turn. Present:

```text
Pull request:    <id>
Title:           <title>
Target branch:   <target>
Findings:        <one-line summary>
Comments posted: <count>, ids: <list>
Proposed vote:   <vote-value>
Reason:          <one paragraph>

Pre-vote checks:
  Test evidence file present: <YES | NO>
  Any blocking comment in this session: <YES | NO>

Risk: HIGH
  Casts your vote on a remote pull request.

Type the vote value back to confirm: approve | approve-with-suggestions
| wait-for-author | reject
```

On confirmation, run:

```bash
az repos pr set-vote --id <prId> --vote <value>
```

Append the vote and timestamp to the findings file `Session log`.

Refusals enforced in this step:

- Refuse `approve` when the test-evidence file is missing or did
  not pass.
- Refuse `approve` when any comment posted in the current session
  was marked blocking by the user.
- In the two cases above, propose `wait-for-author` and post a
  comment requesting test evidence before voting.
- Never call `az repos pr update --auto-complete`.
- Never call `az repos pr set-vote --vote reset` against another
  reviewer's vote.

---

## Hard Guardrails (mirror of ADR-0001)

1. One `az rest POST` per `confirmed-terminal` approval.
2. Mandatory `[AI-assisted review by <UPN>]` prefix on every posted
   comment.
3. Threads created with `status=active` only.
4. No modification of foreign threads.
5. No auto-complete, no merge, no required-reviewer changes.
6. Vote requires a separate-turn explicit confirmation by typing
   the vote value back.
7. Refuse `approve` without test evidence or with blocking comments
   in the session.
