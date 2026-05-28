# Multi-Agent Development Workflow - Feasibility Assessment

| Field | Value |
|---|---|
| Phase | Architecture / Assessment |
| Persona | architect |
| Date | 2026-05-13 |
| Scope | Feasibility of a 5-agent development workflow |
| Constraint | This project has no CI/CD pipeline and none is proposed |
| Output type | Assessment only, no implementation in this task |

---

## 1. Executive Summary

This project has no CI/CD pipeline and none is proposed. Every
enforcement gate that a pipeline would normally provide is shifted
to local deterministic scripts, the existing `confirmed-terminal`
skill, the `.github/copilot-outputs/` evidence artifacts, and the
Azure DevOps required-reviewer policy already implied by
`.github/git-commit-instructions.md`.

| Question | Answer |
|---|---|
| Overall viability | High |
| Should the proposed multi-agent workflow be implemented | Yes, in a hybrid form |
| Recommended implementation style | Hybrid: keep agents only where coordination is needed; use skills, prompts, and a small local script for the rest |
| Highest-value agent | Pull Request Reviewer Agent (advisory, with bounded write capability) |
| Highest-risk agent | Commit Agent (irreversible local action with no CI safety net) |
| Biggest missing prerequisite | A deterministic local pre-flight script that produces a signed test-evidence artifact under `.github/copilot-outputs/` |

Top 5 recommendations:

1. Do not introduce a new "Branch Creator Agent". Implement the
   behaviour as a small PowerShell script plus a thin prompt that
   reuses `confirmed-terminal`. The branch naming rule in
   [.github/git-commit-instructions.md](../git-commit-instructions.md)
   is fully deterministic and does not need an LLM.
2. Keep the existing
   [story-orchestrator.agent.md](../agents/story-orchestrator.agent.md)
   as-is. Do not decompose. Its two approval gates already match
   the constitution.
3. Implement the Commit Agent as a skill plus a prompt that wraps
   the existing
   [azure-devops-commit.prompt.md](../prompts/azure-devops-commit.prompt.md).
   Do not give it autonomy. Require a fresh `confirmed-terminal`
   approval per `git commit` and per `git push`.
4. Implement the Pull Request Creator as a skill that wraps the
   existing
   [azure-devops-pr.prompt.md](../prompts/azure-devops-pr.prompt.md).
   It must refuse to mark a PR as ready when no test-evidence
   artifact exists for the source branch; in that case it creates
   the PR as draft.
5. Implement the Pull Request Reviewer as an advisory agent plus a
   new skill `azure-devops-pr-review`. It is the only proposed
   agent permitted to perform remote writes other than PR
   creation, and is bound by seven hard guardrails (Section 5.5).

ADR required: Yes. Introducing a Pull Request Reviewer Agent that
can post comments and vote on pull requests under the developer's
identity is a new architectural pattern and a new external
integration surface (Azure DevOps REST writes), per the ADR
triggers in [constitution.md](../constitution.md). The ADR is to
be drafted in a follow-up task and is out of scope here.

---

## 2. Evidence Reviewed

| Path | Type | Relevance | Key finding |
|---|---|---|---|
| [.github/copilot-instructions.md](../copilot-instructions.md) | Master config | High | Defines agent inventory, output-logging convention `<BranchName>-<technology>-<phase>-output.md`, and the 4-phase pipeline with two approval gates |
| [.github/constitution.md](../constitution.md) | Non-negotiables | High | Defines ADR triggers, approval gates, "never run git commit/push unless explicitly requested" |
| [.github/git-commit-instructions.md](../git-commit-instructions.md) | Conventions | High | Branch pattern `<JiraIssue>-<UserStoryId>-<Title-With-Proper-Casing>`; commit format `<ID>: <description>` plus bullet list; default reviewers; org `https://dev.azure.com/cswsalesmate`, project `SalesMate` |
| [.github/agents/story-orchestrator.agent.md](../agents/story-orchestrator.agent.md) | Agent | High | Already implements Phases 0-4 with two human-approval gates; explicitly forbids file writes by subagents and forbids running git commit or push |
| [.github/agents/backend/python-fastapi-orchestrator.agent.md](../agents/backend/python-fastapi-orchestrator.agent.md) | Agent | Medium | Backend-scoped orchestrator with conditional architecture gate |
| [.github/agents/frontend/react-orchestrator.agent.md](../agents/frontend/react-orchestrator.agent.md) | Agent | Medium | Frontend-scoped orchestrator |
| [.github/agents/devops/devops-orchestrator.agent.md](../agents/devops/devops-orchestrator.agent.md) | Agent | Medium | Infrastructure-scoped orchestrator |
| [.github/prompts/azure-devops-commit.prompt.md](../prompts/azure-devops-commit.prompt.md) | Prompt | High | Already covers branch and commit message preparation; implements actor-exclusion rule on reviewer list |
| [.github/prompts/azure-devops-pr.prompt.md](../prompts/azure-devops-pr.prompt.md) | Prompt | High | Already wraps `az repos pr create` with fallback to manual instructions when Azure CLI auth is missing |
| [.github/prompts/code-review.prompt.md](../prompts/code-review.prompt.md) | Prompt | Medium | Precedent for the PR Reviewer Agent's findings format |
| [.github/prompts/security-review.prompt.md](../prompts/security-review.prompt.md) | Prompt | Medium | Security checklist reusable by PR Reviewer Agent |
| [.github/skills/confirmed-terminal/SKILL.md](../skills/confirmed-terminal/SKILL.md) | Skill | High | The single approval gate to reuse for every irreversible action |
| [.github/templates/PR_TEMPLATE.md](../templates/PR_TEMPLATE.md) | Template | High | PR description contract used by PR Creator and consumed by PR Reviewer |
| [.github/templates/ADR_TEMPLATE.md](../templates/ADR_TEMPLATE.md) | Template | Medium | ADR contract for the follow-up ADR |
| [.github/CODEOWNERS](../CODEOWNERS) | Policy | Medium | Reviewer routing baseline; uses placeholder team names |
| [scripts/smoke-test.ps1](../../scripts/smoke-test.ps1) | Script | High | Existing local validation pattern. Anchor for the proposed pre-flight script |
| [docs/user-stories.csv](../../docs/user-stories.csv) | Requirements | Medium | 40 stories, ID format `US-NNN`, dependency tracking |
| [docs/user-story-status-matrix.md](../../docs/user-story-status-matrix.md) | Traceability | Medium | Story status assessment, anchored on 2026-04-29 |
| [.github/copilot-outputs/](.) | Convention | High | Existing precedent for evidence artifacts; target directory for both this report and the proposed test-evidence file |

Missing evidence (gaps explicitly acknowledged):

- No `.github/workflows/`, no `azure-pipelines.yml`. Confirmed
  absence; in scope as a constraint, not a gap to fix.
- No `.pre-commit-config.yaml`. Local style enforcement is manual.
- No Azure Boards / work item MCP integration. Story to PR linking
  uses the human-readable ID embedded in branch and commit text.
- No `docs/architecture/decisions/` directory yet, although
  [constitution.md](../constitution.md) references it.

---

## 3. Current Workflow Reconstruction

| # | Step | Current tool / process | Evidence | Pain point | Automation opportunity | Risk |
|---|---|---|---|---|---|---|
| 1 | Story selected | Manual selection from [docs/user-stories.csv](../../docs/user-stories.csv) and [docs/user-story-status-matrix.md](../../docs/user-story-status-matrix.md) | Status matrix assessed 2026-04-29 | Status drift between matrix and Azure Boards | Periodic status sync prompt | Low |
| 2 | Branch created | Manual `git checkout -b ...` per [git-commit-instructions.md](../git-commit-instructions.md) | Branch pattern documented | Naming mistakes, working from a stale base | Local script that fetches base, validates name, creates branch | Low |
| 3 | Implementation planned | Story Orchestrator Phase 1 and Phase 2 | [story-orchestrator.agent.md](../agents/story-orchestrator.agent.md) | Plan quality varies if architect skipped | Conditional architecture gate already exists in tech-specific orchestrators | Low |
| 4 | Code changed | Story Implementer or tech-specific implementer | tech-specific implementer agents | None significant | None needed | Low |
| 5 | Tests run | Developer runs locally, ad hoc | [scripts/smoke-test.ps1](../../scripts/smoke-test.ps1) | No durable proof tests ran or passed | Pre-flight script that writes a test-evidence artifact under `.github/copilot-outputs/` | Medium - no CI gate downstream |
| 6 | Commit created | Manual `git commit` guided by [azure-devops-commit.prompt.md](../prompts/azure-devops-commit.prompt.md) | Prompt enforces commit format | No automated check for secrets, generated files, or stale tests | Commit Agent skill with pre-commit checks plus `confirmed-terminal` | Medium |
| 7 | Branch pushed | Manual `git push` | None | None significant if user runs it | None needed | Low |
| 8 | PR created | [azure-devops-pr.prompt.md](../prompts/azure-devops-pr.prompt.md) plus `az repos pr create` | Prompt implements actor-exclusion | Falls back to manual flow if `az` is not authenticated | PR Creator skill that requires test-evidence file or marks PR as draft | Medium |
| 9 | Review performed | Human reviewers from default reviewer list | [git-commit-instructions.md](../git-commit-instructions.md) | Review depth varies; no AI assistance | PR Reviewer Agent producing a findings file plus per-comment human-approved posting | High value, controlled risk |
| 10 | Validation | Local only; no CI | Confirmed absence of pipeline files | No automated gate; relies entirely on reviewer diligence | Pre-flight script artifact consumed by PR Reviewer Agent | High - this is the structural risk of the no-CI model |
| 11 | Merge decision | Human merge in Azure DevOps | None | None if reviewers do their job | None. Agents must never auto-complete | Low if guardrails hold |

---

## 4. Agent-by-Agent Feasibility Matrix

Scoring rubric: 1 = poor, 5 = excellent. Risk is "1 = safe,
5 = dangerous".

| Agent | Recommended primitive | Value | Risk | Complexity | Fit | Permissions | Integrations | Human approval | Recommendation |
|---|---|---|---|---|---|---|---|---|---|
| Branch Creator | Local PowerShell script + thin prompt | 3 | 2 | 1 | 4 | Local git only | git CLI | Per branch creation, via `confirmed-terminal` | Implement as script, not agent |
| Story Orchestrator | Agent (already exists) | 5 | 1 | n/a | 5 | None beyond local file edits and subagent invocation | None | Two gates per story (post-architecture, post-planning) | Keep as-is |
| Commit Agent | Skill + prompt | 4 | 4 | 2 | 5 | Local git only | git CLI, optional `gitleaks`-style local secret scan | Per commit, via `confirmed-terminal` | Implement as skill |
| Pull Request Creator | Skill wrapping existing prompt | 4 | 3 | 2 | 5 | Azure DevOps Contributor on `SalesMate` repo | `az repos pr create`, [PR_TEMPLATE.md](../templates/PR_TEMPLATE.md) | Per PR creation, via `confirmed-terminal`; auto-draft if test evidence missing | Implement as skill |
| Pull Request Reviewer | Advisory agent + new skill | 5 | 4 | 4 | 5 | Azure DevOps Contributor on `SalesMate` repo (post threads, set vote); explicitly refuses Bypass policies, Force push, Manage permissions | `az account show`, `az repos pr list/show`, `az rest threads`, `az repos pr set-vote`, local `git diff` | Per comment AND a separate-turn per-vote confirmation | Implement as agent, conditional on the seven guardrails in Section 5.5 |

No row recommends "CI policy" because no CI exists in this project.

---

## 5. Detailed Agent Assessment

### 5.1 Branch Creator

**Purpose.** Create and check out a feature branch for a selected
story or work item, using the project's deterministic naming rule.

**Recommended implementation type.** Local PowerShell script under
`scripts/` plus a thin prompt that invokes it. Not an agent.

**Why this fits the project.** The branch naming rule in
[git-commit-instructions.md](../git-commit-instructions.md) is
fully deterministic: `<JiraIssue>-<UserStoryId>-<Title-With-Proper-Casing>`.
A scripted regex-validated builder is more reliable, faster, and
cheaper than an LLM. The existing
[scripts/smoke-test.ps1](../../scripts/smoke-test.ps1) is the
template for adding a sibling `scripts/new-branch.ps1`.

**Required inputs.** Jira issue key, user story id, short title,
target base branch (defaults to `master`).

**Expected outputs.** Local branch created and checked out from a
freshly fetched base. A one-line summary printed to the terminal.
No remote write.

**Tool access required.** `git`, PowerShell.

**Permissions required.** Local repo only.

**Guardrails.** The script must:

- Refuse to run when `git status` reports uncommitted changes,
  unless invoked with `-Force` and after `confirmed-terminal`.
- Always run `git fetch` on the base before branching.
- Validate the produced name against the regex implied by the
  convention.
- Refuse to overwrite an existing local branch with the same name.
- Never `git push` the branch. Push is a separate, later step.

**Human approval points.** One, before running the script, via
`confirmed-terminal`.

**Failure modes.** Invalid inputs (mitigated by regex validation);
stale base branch (mitigated by mandatory fetch); name collision
(mitigated by existence check).

**Compensating control in absence of CI.** None needed; this step
has no CI dependency in any project.

**Acceptance criteria.** Script exits non-zero on any guardrail
violation. Successful run leaves the working tree on the new
branch with no uncommitted changes.

**Go / No-Go.** Go, as a script, not as an agent.

---

### 5.2 Story Orchestrator

**Purpose.** Coordinate the four story phases (architecture,
planning, implementation, QA) with explicit human gates.

**Recommended implementation type.** Agent. Already implemented at
[story-orchestrator.agent.md](../agents/story-orchestrator.agent.md)
with tech-specific variants under
[.github/agents/backend/](../agents/backend/),
[.github/agents/frontend/](../agents/frontend/), and
[.github/agents/devops/](../agents/devops/).

**Why this fits the project.** Coordination across architect,
planner, implementer, and QA subagents is a genuine multi-step
problem with conditional branches (architecture gate, rework loop)
that benefit from an LLM. The two approval gates align with the
constitution.

**Required inputs.** User story, acceptance criteria, scope.

**Expected outputs.** A lifecycle report under
`.github/copilot-outputs/<branch>-<tech>-<phase>-output.md` and a
synthesized summary in chat.

**Tool access required.** `runSubagent`, file edit tools, no
terminal write capability for git.

**Permissions required.** Local file system.

**Guardrails.** Already enforced in the agent contract:

- Never run `git commit` or `git push`.
- Never delegate file writes to a subagent.
- Always wait for explicit user approval at Gate 1 and Gate 2.

**Human approval points.** Two per story (post-architecture,
post-planning).

**Failure modes.** Subagent output drift (mitigated by structured
handoff sections); approval fatigue (mitigated by concise gate
summaries).

**Compensating control in absence of CI.** Phase 4 QA review
substitutes for what a CI test-result gate would otherwise enforce.
The QA agent must produce a pass/fail verdict in the output file.

**Acceptance criteria.** No change to current behaviour. Keep
as-is.

**Go / No-Go.** Go. Already in production. Do not decompose.

---

### 5.3 Commit Agent

**Purpose.** Stage logical groups of changes and produce a commit
message conforming to the project template, with safety checks.

**Recommended implementation type.** Skill plus a prompt. Not an
agent. Wraps the existing
[azure-devops-commit.prompt.md](../prompts/azure-devops-commit.prompt.md).

**Why this fits the project.** Commit message format is fully
specified. The variability is in change grouping and sensitive-file
detection, which a small skill can handle deterministically with a
short LLM-assisted summary step.

**Required inputs.** Working tree state, story id, optional list
of intended logical groups.

**Expected outputs.** Proposed `git add` plan, proposed commit
message, list of detected risks (secrets, generated files, stale
tests). Nothing is executed without approval.

**Tool access required.** `git`, terminal, optional local secret
scanner if installed.

**Permissions required.** Local repo only.

**Guardrails.**

- Never `git commit` without a fresh `confirmed-terminal` approval.
- Never commit files matching `.env*`, `*.pem`, `*.key`, `*.pfx`,
  `*.crt`, `id_rsa*`, or any path under `infra/nginx/certs/`.
- Never amend or squash existing commits unless the user explicitly
  asks for it in the same turn.
- Never bypass pre-commit hooks (no `--no-verify`).
- Always print the staged file list and the exact commit message
  before requesting approval.
- Refuse to commit if a sibling test-evidence file is missing under
  `.github/copilot-outputs/` for the current branch, unless the
  user overrides with an explicit acknowledgement.

**Human approval points.** One per commit. Push is a separate
approval, separately gated.

**Failure modes.** Accidental secret commit (mitigated by deny
list); over-broad commits (mitigated by mandatory grouping
proposal); message format drift (mitigated by template enforcement).

**Compensating control in absence of CI.** The pre-commit
test-evidence check is the local substitute for a CI test gate.
The skill refuses to proceed when evidence is missing.

**Acceptance criteria.** Skill never executes a remote write. Skill
produces a deterministic refusal message when guardrails block the
commit.

**Go / No-Go.** Go, as a skill. This is the highest-risk component
because the action is local but irreversible without `git reset`,
and there is no downstream CI safety net.

---

### 5.4 Pull Request Creator

**Purpose.** Create the pull request in Azure DevOps using the
project conventions.

**Recommended implementation type.** Skill that wraps the existing
[azure-devops-pr.prompt.md](../prompts/azure-devops-pr.prompt.md).
Not a new agent.

**Why this fits the project.** The prompt already encodes the
organization, project, default reviewers, actor-exclusion rule,
and the `az repos pr create` fallback flow. A skill formalises the
input and output and adds the test-evidence precondition.

**Required inputs.** Source branch, target branch (default
`master`), commits, linked work item id (parsed from branch name),
[PR_TEMPLATE.md](../templates/PR_TEMPLATE.md) sections.

**Expected outputs.** A draft or ready PR in Azure DevOps with the
title format `<JiraIssue> <UserStoryId>: <title>`, the template
sections populated, default reviewers minus the actor, and the
work item linked.

**Tool access required.** `az repos pr create`, `git` for branch
state queries, file read for the test-evidence artifact.

**Permissions required.** Azure DevOps Contributor on the
`SalesMate` repo.

**Guardrails.**

- Always confirm source and target branch in the approval prompt.
- Refuse to create a PR if the source branch is not pushed.
- Auto-mark the PR as draft when the test-evidence artifact for
  the source branch is missing under `.github/copilot-outputs/`.
- Never auto-complete and never set merge options.
- Never assign reviewers outside the default list plus
  [CODEOWNERS](../CODEOWNERS) routing, and always exclude the
  actor.
- Always print the final title, description, source, target, work
  item id, and reviewer list before approval.

**Human approval points.** One per PR creation, via
`confirmed-terminal`.

**Failure modes.** Wrong target branch (mitigated by approval
display); reviewer leakage (mitigated by actor exclusion); missing
work item link (mitigated by branch-name parsing and refusal if
parsing fails).

**Compensating control in absence of CI.** The auto-draft rule is
the local substitute for a CI build-validation status check.
Reviewers see "Draft" and know test evidence is incomplete.

**Acceptance criteria.** Skill produces a valid PR or a clear
refusal with the missing precondition named.

**Go / No-Go.** Go.

---

### 5.5 Pull Request Reviewer

**Purpose.** Assist human reviewers by discovering assigned PRs,
producing a structured findings file, posting comments under
explicit per-comment approval, and casting a vote under a separate
explicit per-vote approval.

**Recommended implementation type.** Advisory agent
`pull-request-reviewer.agent.md` plus a new skill
`azure-devops-pr-review/SKILL.md`.

**Why this fits the project.** Review is the highest-leverage
human activity in a no-CI workflow. AI assistance produces the
largest quality lift here. The Azure CLI surface is sufficient
without any MCP server.

**Required inputs.** None at invocation. The agent discovers its
queue from `az account show` and
`az repos pr list --reviewer @me --status active`.

**Expected outputs.** A findings file at
`.github/copilot-outputs/<branch>-pr-review-output.md` per PR,
plus zero or more posted comment threads, plus zero or one vote.
The findings file always ends with a "Session log" section listing
posted thread ids and the final vote, so the action is auditable.

**Tool access required.** `az account show`, `az repos pr list`,
`az repos pr show`, `az rest` for thread read and write,
`az repos pr set-vote`, local `git fetch` and `git diff`, file
write for the findings file.

**Permissions required.** Azure DevOps Contributor on the
`SalesMate` repo. Explicitly refuses to use Bypass policies, Force
push, Manage permissions, or Administer pull requests, even if the
signed-in identity holds them.

**Seven hard guardrails.**

1. Never batch comment approvals. One `az rest POST` per
   `confirmed-terminal` approval.
2. Every posted comment body is prefixed with
   `[AI-assisted review by <UPN from az account show>]`.
3. New threads are created with `status=active` only. The agent
   cannot pre-close its own threads.
4. The agent never resolves, reactivates, replies in, or otherwise
   modifies threads it did not author.
5. The agent never calls `az repos pr update --auto-complete`,
   never merges, never disables required reviewers.
6. The vote step is gated behind a second, distinct user turn that
   shows the PR id, title, target branch, findings summary, list
   of comments posted in this session, and the literal vote value.
   The user must type the vote value back (or a clear "approve" or
   "reject") before the agent runs `az repos pr set-vote`. No
   default, no implicit approval.
7. The agent must refuse to propose `approve` when any comment it
   posted in this session was marked blocking by the user, or when
   no test-evidence file exists for the source branch under
   `.github/copilot-outputs/`. In those cases the proposed vote
   is forced to `wait-for-author` and the agent posts a comment
   requesting test evidence.

**Human approval points.** One per posted comment, plus one
separate-turn approval for the vote. Read-only steps require no
approval because they have no remote side effect.

**Failure modes and mitigations.**

| Failure mode | Mitigation |
|---|---|
| Azure CLI not signed in | Stop at step 1; instruct user to run `az login` |
| Wrong comment posted | Per-comment approval; deletion of own thread requires a fresh approval |
| Wrong vote cast | Second-turn explicit confirmation; user can manually `az repos pr set-vote --vote reset` |
| AI comment mistaken for human | Mandatory `[AI-assisted review by <UPN>]` prefix |
| Foreign thread tampering | Hard refusal; the agent contract has no code path that calls `PATCH .../threads/{id}` for threads where `author.uniqueName != actor UPN` |
| Approval over PR with no test evidence | Pre-vote check refuses `approve`; forces `wait-for-author` |

**Compensating control in absence of CI.** The findings file is
the durable evidence artifact a CI status check would otherwise
provide. The pre-vote test-evidence check is the local substitute
for a CI build-validation gate. Together these two controls cover
the structural gap of having no automated PR validation.

**Acceptance criteria.** No vote without an explicit second-turn
confirmation. No comment posted without a `confirmed-terminal`
approval. Every posted comment is traceable in the findings file
session log.

**Go / No-Go.** Go, conditional on all seven guardrails being
encoded in the agent contract before first use, and on the ADR
being drafted as a follow-up task.

---

## 6. Recommended Workflow of Good Agent Usage

### Phase 0 - Preconditions

- Working tree is clean.
- Story id is selected from
  [docs/user-stories.csv](../../docs/user-stories.csv) and status
  matrix.
- Acceptance criteria are available.
- Target branch is `master` unless the story specifies otherwise.
- `az` is signed in for any Azure DevOps interaction
  (`az account show` succeeds).
- `confirmed-terminal` is loaded.

### Phase 1 - Branch creation

- Developer invokes the branch script (not an agent).
- Script proposes the branch name, prints the exact `git` commands,
  and waits for `confirmed-terminal` approval.
- On approval the script fetches the base, validates the name,
  refuses on collision or stale base, and creates and checks out
  the branch.
- No remote push.

### Phase 2 - Story planning

- Developer invokes the appropriate orchestrator (Project Manager
  routes by module).
- Orchestrator runs Phase 1 (architecture) and presents Gate 1.
- Developer approves before planning starts.
- Orchestrator runs Phase 2 (planning) and presents Gate 2.
- Developer approves before any code is changed.

### Phase 3 - Implementation

- Implementer agent applies file changes directly.
- Orchestrator updates the lifecycle output file as it goes.
- Developer reviews diffs.

### Phase 4 - Test and validation

- Developer runs the project test commands locally.
- Test results are written to a sibling file under
  `.github/copilot-outputs/<branch>-<tech>-test-evidence.md`,
  with the literal pass/fail verdict, command lines, and a short
  summary. This file is the no-CI substitute for a build-validation
  status check and is consumed by the Commit Agent, the PR Creator
  Skill, and the PR Reviewer Agent.
- If tests fail, the orchestrator proposes fixes and the loop
  continues. Failures are never hidden.

### Phase 5 - Commit preparation

- Developer invokes the Commit Agent skill.
- Skill inspects staged and unstaged changes, proposes logical
  commit grouping, runs the secret deny-list, and verifies the
  test-evidence file exists for the current branch.
- Skill prints the final staged file list and commit message.
- Developer approves via `confirmed-terminal`. Skill runs
  `git commit`. One approval per commit.

### Phase 6 - Push and PR creation

- Developer pushes the branch (or approves an agent-assisted push
  via a separate `confirmed-terminal` gate).
- Developer invokes the PR Creator skill.
- Skill builds title, description, reviewer list (default minus
  actor), linked work item, and source/target.
- If the test-evidence file is missing or stale, the skill marks
  the PR as draft.
- Skill prints the full proposal and waits for approval.
- On approval, skill runs `az repos pr create`.

### Phase 7 - Assisted review

- Reviewer invokes the PR Reviewer Agent.
- Agent runs the read-only sweep: `az account show`,
  `az repos pr list --reviewer @me`, `az repos pr show`,
  `az rest GET .../threads`, local `git diff`, write the findings
  file.
- Agent presents a numbered list of proposed comments and a
  proposed vote.
- Reviewer approves, edits, or skips each comment. Approved
  comments are posted one at a time with the AI-assisted prefix.
- In a separate turn, reviewer confirms or overrides the vote
  value. Agent runs `az repos pr set-vote`.

### Phase 8 - Feedback loop

- PR author addresses comments.
- Story Orchestrator or the relevant tech-specific implementer
  helps implement fixes.
- Commit Agent skill creates follow-up commits.
- PR Reviewer Agent re-runs the sweep on the delta only and
  produces an updated findings file.

### Phase 9 - Merge readiness

- Reviewer checks: required reviewers approved in Azure DevOps
  (this is the no-CI substitute for build-validation policy);
  comments resolved by the human author; work item linked; PR not
  in draft state.
- No agent ever auto-completes, auto-merges, or marks the PR
  ready-to-merge on the developer's behalf.

---

## 7. Recommended `.github/agents` Structure

Target tree after the workflow is implemented in a follow-up task.
Existing files are unchanged. New files are marked `(new)`.

```text
.github/
  agents/
    project-manager.agent.md
    story-orchestrator.agent.md
    story-architect.agent.md
    story-planner.agent.md
    story-implementer.agent.md
    story-qa-review.agent.md
    general-purpose.agent.md
    pull-request-reviewer.agent.md            (new)
    backend/
      python-fastapi-orchestrator.agent.md
      python-fastapi-planner.agent.md
      python-fastapi-implementer.agent.md
      python-fastapi-qa.agent.md
    frontend/
      react-orchestrator.agent.md
      react-planner.agent.md
      react-implementer.agent.md
      react-qa.agent.md
    devops/
      devops-orchestrator.agent.md
      devops-planner.agent.md
      devops-implementer.agent.md
      devops-qa.agent.md
      deployment-smoke-check.agent.md
  skills/
    confirmed-terminal/SKILL.md
    adr-writer/SKILL.md
    dependency-update/SKILL.md
    framework-fetcher/SKILL.md
    requirements-to-tests/SKILL.md
    ai-prompt-contract-design/SKILL.md
    commit-preparation/SKILL.md               (new)
    azure-devops-pr-create/SKILL.md           (new)
    azure-devops-pr-review/SKILL.md           (new)
  prompts/
    azure-devops-commit.prompt.md
    azure-devops-pr.prompt.md
    code-review.prompt.md
    security-review.prompt.md
    review-pr.prompt.md                       (new, invokes the PR Reviewer Agent)
    prepare-commit.prompt.md                  (new, invokes the Commit skill)
  instructions/
    git-workflow.instructions.md              (new, codifies the no-CI gates)
    azure-devops.instructions.md              (new, codifies the az CLI surface and refusals)
  templates/
    PR_TEMPLATE.md
    ADR_TEMPLATE.md
    FEATURE_SPEC_TEMPLATE.md
    prompt_template.md
    test-evidence-template.md                 (new)
  copilot-outputs/
    <branch>-<tech>-<phase>-output.md
    <branch>-<tech>-test-evidence.md          (new, written by Phase 4)
    <branch>-pr-review-output.md              (new, written by PR Reviewer)
scripts/
  smoke-test.ps1
  new-branch.ps1                              (new, replaces the Branch Creator agent)
  preflight.ps1                               (new, writes the test-evidence file)
docs/
  architecture/
    decisions/
      ADR-NNNN-pull-request-reviewer-agent.md (new, follow-up task)
```

No GitHub Actions, no Azure Pipelines, no pre-commit hooks. All
gates are local or human.

---

## Session log

- Plan source: `/memories/session/plan.md`.
- Persona: architect.
- No code or configuration was changed in this task.
- No git operations were performed.
- Output file: this document, at
  `.github/copilot-outputs/agentic-workflow-feasibility-output.md`.
- Follow-up tasks identified: (a) draft ADR for the PR Reviewer
  Agent under `docs/architecture/decisions/`; (b) implement the
  three new skills, the new agent, the two new prompts, the two
  new instructions files, and the two new scripts.
