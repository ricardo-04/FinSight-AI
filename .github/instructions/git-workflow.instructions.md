---
applyTo: "**"
---

# Instructions - Git Workflow (No-CI)

## Scope

These rules apply to every git operation in the SalesMate
repository. The project has no CI/CD pipeline. All gates that a
pipeline would normally enforce are local, scripted, or human.

These rules complement, and never override,
`.github/git-commit-instructions.md` and
`.github/constitution.md`.

---

## Branch Creation

- Users invoke the
  [Branch Creator](../agents/branch-creator.agent.md) agent for
  branch creation.
- The Branch Creator agent must call the script at
  [scripts/new-branch.ps1](../../scripts/new-branch.ps1). The
  script is the deterministic implementation of the branch naming
  rule in `.github/git-commit-instructions.md`.
- The script must be invoked through the `confirmed-terminal`
  skill. The agent must show the exact PowerShell command before
  execution.
- Never create a branch when the working tree has uncommitted
  changes, unless the script is invoked with `-Force` and the user
  approves the override.
- Always fetch the base branch before creating the new branch.
- Never create a branch under a protected namespace
  (`master`, `release/*`, `hotfix/*`) without an explicit, in-turn
  user request.

---

## Commit

- Users invoke the [Commit Agent](../agents/commit-agent.agent.md)
  for commit preparation.
- The Commit Agent must load the
  [commit-preparation](../skills/commit-preparation/SKILL.md)
  skill for every commit. The
  [prepare-commit](../prompts/prepare-commit.prompt.md) prompt is
  still available as a lower-level shortcut.
- Never run `git commit --no-verify`.
- Never amend or squash existing commits unless the user requests
  it in the same turn.
- The commit message format is non-negotiable; see
  `.github/git-commit-instructions.md`.
- Refuse to commit when the secret deny-list, the forbidden-file
  deny-list, or the in-progress operation check fails.

---

## Test Evidence (No-CI Substitute)

- Run [scripts/preflight.ps1](../../scripts/preflight.ps1) before
  every commit that changes runtime code or tests. The script
  produces a file at
  `.github/copilot-outputs/<branch>-<tech>-test-evidence.md` with
  the literal verdict line `Result: PASS` or `Result: FAIL`.
- The Commit Preparation skill, the Azure DevOps PR Create skill,
  and the Pull Request Reviewer Agent all consume this file. When
  it is missing or did not pass, downstream actions either refuse,
  warn, or downgrade the action (for example, draft PR, vote
  forced to `wait-for-author`).
- The test-evidence file is the no-CI substitute for a build-
  validation status check.

---

## Push

- Push is always a separate, separately approved action. Never
  combine push with commit in a single approval.
- Use `git push --set-upstream origin <branch>` for the first push
  on a branch.
- Never use `git push --force` or `git push --force-with-lease`
  without an explicit in-turn user request.
- When the user asks to use `rsa_salesmate`, wrap push with:

  ```bash
  GIT_SSH_COMMAND='ssh -i ~/.ssh/rsa_salesmate -o IdentitiesOnly=yes'
  ```

---

## Pull Request

- Create pull requests with the
  [azure-devops-pr-create](../skills/azure-devops-pr-create/SKILL.md)
  skill.
- The skill auto-marks the pull request as draft when the test-
  evidence file is missing or did not pass.
- Never auto-complete a pull request.
- Never assign reviewers outside the default list in
  `.github/git-commit-instructions.md` plus `.github/CODEOWNERS`
  routing, and always exclude the actor.

---

## Review

- Use the
  [Pull Request Reviewer](../agents/pull-request-reviewer.agent.md)
  agent to assist human review. The agent never replaces human
  review, never approves without an explicit user-typed vote, and
  never modifies threads it did not author.

---

## Merge

- Merge is always performed by a human in Azure DevOps after the
  required reviewers have approved. No agent merges.
