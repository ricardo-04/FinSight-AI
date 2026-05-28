# PR Review Findings

**PR ID:** 10
**Title:** AIAPMMWP1: Improve GitHub Copilot folder organization and structure
**Author:** caferreira@criticalsoftware.com
**Source branch:** AIAPMMWP1-Improve-Github-Copilot-Folder-Organization-And-Struture
**Target branch:** master
**Status:** Active (Draft)
**Reviewers:** dsmendes, ra-pombo, pmfmonteiro
**Reviewed by:** ra-pombo@criticalsoftware.com
**Date:** 2026-05-13

---

## Summary

This PR reorganizes and extends the `.github` folder with new agents,
skills, prompts, instructions, and scripts to improve the Copilot-assisted
development workflow. It also removes the mcp-atlassian submodule from
tracking and updates `.vscode/mcp.json`.

**Changed files (27):**
- `.github/agents/`: branch-creator, commit-agent, pull-request-reviewer
- `.github/skills/`: commit-preparation, azure-devops-pr-create, azure-devops-pr-review
- `.github/prompts/`: prepare-commit, review-pr (new); azure-devops-commit, azure-devops-pr (updated)
- `.github/instructions/`: azure-devops.instructions.md, git-workflow.instructions.md (new)
- `.github/templates/`: test-evidence-template.md (new); PR_TEMPLATE.md (updated)
- `scripts/`: new-branch.ps1, preflight.ps1 (new)
- `docs/architecture/decisions/`: ADR-0001-pull-request-reviewer-agent.md (new)
- `.vscode/mcp.json`: Updated
- `.env.example`, `.gitignore`: Minor updates

---

## Linked Work Item

Parsed from branch name: **AIAPMMWP1** (no US-NNN story ID present in branch name).

---

## Risk-ranked Findings

### [HIGH] ADR-0001 status is still "Proposed" (Thread 35 - pmfmonteiro)

**File:** `docs/architecture/decisions/ADR-0001-pull-request-reviewer-agent.md`

The ADR Status field reads `Proposed`. The constitution requires the ADR
status to be set to `Accepted` before the implementing PR merges. The PR
implements the Pull Request Reviewer Agent, which is the subject of this ADR.
Must be resolved before merge.

**Fix:** Change `**Status:** Proposed` to `**Status:** Accepted` in ADR-0001.

---

### [HIGH] .vscode/mcp.json tracked by git with developer-specific paths (Thread 34 - pmfmonteiro)

**File:** `.vscode/mcp.json`

The file is committed to git and currently contains a `wsl.exe` command
with `${workspaceFolder}` references. Every developer cloning the repo
will receive this config. If the submodule or `.venv` path is absent on
their machine, the MCP server will fail silently. The PR description does
not document this as intentional.

**Recommended fix:** Add `.vscode/mcp.json` to `.gitignore` and provide
a `.vscode/mcp.json.example` with placeholder paths. Consistent with how
`.env` is treated.

---

### [MEDIUM] story-orchestrator.agent.md still references mcp-atlassian and bitbucket tools (Threads 31/33 - pmfmonteiro)

**File:** `.github/agents/story-orchestrator.agent.md` (line 5)

```
tools: [..., 'bitbucket/*', 'mcp-atlassian/*', ...]
```

The PR removes mcp-atlassian from tracking via `.gitignore`. When the
submodule is absent, VS Code Copilot will fail to resolve these tool
references and the Story Orchestrator invocation will report an unresolved
tool.

**Fix:** Remove `'mcp-atlassian/*'` and `'bitbucket/*'` from the tools
list in `story-orchestrator.agent.md`.

---

### [INFO] PR is marked Draft

The PR was created as a draft. Before requesting a vote, the author
should mark it as ready for review.

---

## Proposed Comments

1. **[PR-LEVEL] ADR-0001 status** - Request change of status from Proposed to Accepted.
   - Blocking: Yes
2. **[FILE] .vscode/mcp.json** - Request .gitignore entry and .example file.
   - Blocking: No (recommendation)
3. **[FILE] story-orchestrator.agent.md line 5** - Remove mcp-atlassian/* and bitbucket/* from tools list.
   - Blocking: Yes

---

## Pre-vote Checks

- Test evidence file: not applicable (no runtime code changed)
- Blocking comments in this session: pending (see proposed comments above)
- Existing blocking threads from pmfmonteiro: 3 open (threads 31, 34, 35)

---

## Proposed Vote

**`wait-for-author`**

Reason: Threads 31, 34, and 35 from pmfmonteiro are unresolved. Finding
[HIGH] on ADR-0001 status and the mcp.json tracking issue must be
addressed before approving. Once the author resolves those threads and
updates ADR-0001 to Accepted, the vote can be reconsidered.

---

## Session Log

| # | Thread ID | Type | Summary | Blocking |
|---|---|---|---|---|
| 1 | 36 | PR-level | ADR-0001 status must be Accepted before merge | Yes |
| 2 | 37 | PR-level | .vscode/mcp.json tracked by git - recommend .gitignore + .example | No |
