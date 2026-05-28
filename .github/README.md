# Project Copilot Configuration

This folder contains the GitHub Copilot configuration for the project.
It is the **single source of truth** for all AI agent instructions, personas,
skills, prompts, workflows, output artifacts, and templates.

---

## Reading Order

| Audience | Start here | Then read |
|---|---|---|
| New to the project | `GETTING_STARTED.md` | `copilot-instructions.md` |
| Existing developer | `copilot-instructions.md` | Relevant `instructions/*.instructions.md` |
| Admin or customizer | `constitution.md` | `agents/`, `personas/`, `skills/` |

Key precedence: `constitution.md` overrides all other files where they conflict.

---

## Requirements

- Visual Studio Code
- GitHub Copilot extension
- GitHub Copilot Chat extension

---

## What is in this folder

| Folder / File | Purpose |
|---|---|
| `agents/` | Custom agent definitions for each technology domain |
| `agents/branch-creator.agent.md` | Thin branch creation facade over `scripts/new-branch.ps1` |
| `agents/commit-agent.agent.md` | Thin commit facade over the Commit Preparation skill |
| `agents/project-manager.agent.md` | Entry point - routes every request to the correct agent |
| `agents/story-*.agent.md` | Lifecycle agents for cross-cutting stories |
| `agents/frontend/` | React frontend agents |
| `agents/backend/` | Python FastAPI backend agents |
| `agents/devops/` | DevOps and deployment infrastructure agents |
| `agents/pull-request-reviewer.agent.md` | Assisted Azure DevOps pull request review |
| `agents/general-purpose.agent.md` | Scripts, file manipulation, utility tasks |
| `instructions/` | File-scoped coding conventions loaded by VS Code |
| `personas/` | Role definitions used by agents |
| `skills/` | Reusable knowledge packages loaded on demand |
| `templates/` | Document templates for ADRs, PRs, feature specs |
| `prompts/` | Reusable prompt files invocable from Copilot Chat |
| `copilot-outputs/` | Required AI phase output and test-evidence artifacts |
| `constitution.md` | Non-negotiable project rules |
| `copilot-instructions.md` | Main configuration |
| `git-commit-instructions.md` | Commit message format |
| `CODEOWNERS` | Maps modules to responsible teams |

---

## Skill Portfolio

| Skill | Use |
|---|---|
| `adr-writer` | Produce ADRs for significant architecture decisions |
| `confirmed-terminal` | Apply the user approval gate before terminal commands |
| `commit-preparation` | Prepare a safe git commit with local checks |
| `azure-devops-pr-create` | Create Azure DevOps pull requests safely |
| `azure-devops-pr-review` | Review assigned Azure DevOps pull requests |
| `dependency-update` | Update Python and npm dependencies with audit checks |
| `framework-fetcher` | Verify version-specific framework APIs and deprecations |
| `requirements-to-tests` | Map acceptance criteria to tests and coverage gaps |
| `ai-prompt-contract-design` | Design structured runtime AI prompt output contracts |

---

## How to use

### Starting a task

Open Copilot Chat in Agent mode and select **Project Manager**. Type your
request and it will route to the correct orchestrator.

Examples:

```
Add a new REST endpoint to return opportunity statistics
```

```
Create a new React screen for template management
```

```
Update docker-compose.yml to add a new service
```

### The 4-phase pipeline

Every task follows this pipeline automatically:

```
Phase 1: Architecture  (Architect agent assesses ADR need)
         |
         | You review and approve
         v
Phase 2: Planning  (Planner agent produces implementation plan)
         |
         | You review and approve
         v
Phase 3: Development  (Implementer agent writes code and tests)
         |
         v
Phase 4: QA Review  (QA agent validates against acceptance criteria)
```

At each approval gate the agent pauses and waits for your confirmation.

### Implementing an existing user story

For the full existing-story flow, see
[GETTING_STARTED.md](GETTING_STARTED.md#implementing-an-existing-user-story).

Daily sequence:

```text
Branch Creator
  -> Story Orchestrator
  -> local preflight
  -> Commit Agent
  -> push branch
  -> Azure DevOps PR Create skill
  -> Pull Request Reviewer
  -> human merge
```

---

## VS Code Configuration

Enable Agent mode in VS Code settings:

```json
{
  "chat.agent.enabled": true,
  "github.copilot.chat.agent.thinkingTool": true
}
```

Select **Project Manager** from the agent selector in the Copilot Chat panel
to activate the full pipeline.
