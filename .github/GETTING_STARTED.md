# Getting Started - AI Agent Pipeline for Software Development

## What is this?

This is a complete AI-powered development pipeline for GitHub Copilot that implements a structured 4-phase workflow for software development tasks:

1. **Architecture Phase** - Evaluates technical impact and decides if an ADR is needed
2. **Planning Phase** - Creates detailed implementation plans with file-level breakdown
3. **Development Phase** - Writes code and tests following project conventions
4. **QA Review Phase** - Validates changes against acceptance criteria

The system includes specialized agents for different technologies (React, Python FastAPI, DevOps) and automatically routes requests to the correct agent based on the module and task type.

---

## Why use this?

- **Consistency**: All code follows the same standards and conventions
- **Quality**: Built-in code review and testing validation at every step
- **Documentation**: ADRs and implementation plans are generated automatically
- **Safety**: Approval gates prevent unwanted changes
- **Specialization**: Domain experts for each technology stack
- **Traceability**: Every change is linked to user stories and tracked

---

## What's included?

```
.github/
├── agents/                      # AI agent definitions by domain
│   ├── project-manager.agent.md # Entry point - routes all requests
│   ├── story-*.agent.md         # Generic lifecycle agents
│   ├── frontend/                # React agents
│   ├── backend/                 # Python FastAPI agents
│   └── devops/                  # Infrastructure agents
├── instructions/                # File-scoped coding rules
│   ├── react-frontend.instructions.md
│   ├── python-fastapi-backend.instructions.md
│   ├── devops-deployment.instructions.md
│   └── security.instructions.md
├── personas/                    # Role definitions (developer, QA, etc.)
├── skills/                      # Reusable knowledge modules
├── templates/                   # Document templates (ADR, PR, etc.)
├── constitution.md              # Non-negotiable project rules
├── copilot-instructions.md      # Main configuration
└── README.md                    # Overview of the folder structure
```

---

## Prerequisites

1. **Visual Studio Code** (latest version)
2. **GitHub Copilot** extension (with agent mode enabled)
3. **GitHub Copilot Chat** extension
4. Active **GitHub Copilot** subscription

### Azure DevOps pull request publishing

Azure CLI is required only when an agent is explicitly asked to create or
update Azure DevOps pull requests from the terminal. The prompts still
provide manual pull request fields when Azure CLI is not installed or the
user is not authenticated.

Install Azure CLI and the Azure DevOps extension using one of the options
below.

**Windows with winget**

```powershell
winget install --exact --id Microsoft.AzureCLI
az extension add --name azure-devops
az login
az devops configure --defaults organization=https://dev.azure.com/cswsalesmate project=SalesMate
```

**Windows with MSI installer**

```powershell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindowsx64 -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
az extension add --name azure-devops
az login
az devops configure --defaults organization=https://dev.azure.com/cswsalesmate project=SalesMate
```

**Windows with WSL Ubuntu**

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az extension add --name azure-devops
az login
az devops configure --defaults organization=https://dev.azure.com/cswsalesmate project=SalesMate
```

For browserless authentication, use the Azure DevOps login command and
enter a Personal Access Token when prompted:

```bash
az devops login --organization https://dev.azure.com/cswsalesmate
```

Never commit Personal Access Tokens, credentials, private keys, or token
values to repository files.

---

## Quick Start

### Step 1: Enable Agent Mode in VS Code

Open VS Code settings (`Ctrl+,` or `Cmd+,`) and add:

```json
{
  "chat.agent.enabled": true,
  "github.copilot.chat.agent.thinkingTool": true
}
```

### Step 2: Install this configuration

Copy the `.github` folder to your project root. You have two options:

**Option A: Direct copy** (for a single project)
```bash
cp -r /path/to/this/.github /path/to/your/project/.github
```

**Option B: Symbolic link** (recommended for multiple projects)
```bash
# Linux/macOS
ln -s /path/to/this/.github /path/to/your/project/.github

# Windows (PowerShell as Administrator)
New-Item -ItemType SymbolicLink -Path "C:\path\to\your\project\.github" -Target "C:\path\to\this\.github"
```

Using symbolic links allows you to maintain a single source of truth - changes to one `.github` folder are immediately reflected in all linked projects.

### Step 3: Select the Project Manager agent

1. Open GitHub Copilot Chat in VS Code
2. Click the mode selector at the bottom of the chat panel
3. Choose **"Project Manager"** from the agent list
4. The 4-phase pipeline is now active

### Step 4: Test it

Try a simple request:

```
Create a new REST endpoint that returns opportunity statistics
```

The Project Manager will analyze the request, route it to the Python FastAPI Orchestrator, and guide you through architecture, planning, development, and QA phases.

---

## Implementing an Existing User Story

Use this flow when the user story already exists in the backlog,
Azure Boards, or `docs/user-stories.csv`.

First create a story branch with **Branch Creator**. Then start the
implementation with **Story Orchestrator**. If the story scope is
unclear, select **Project Manager** and let it route the request.

### Step 1: Create the Story Branch

Open Copilot Chat in Agent mode and select **Branch Creator**.
Provide the Jira issue, story ID, story title, and optional base
branch.

Example:

```text
Create a branch for AIAPMMWP1-22 US-020 Document conversion and
RustFS integration supporting S4.
```

The agent builds the `scripts/new-branch.ps1` command, shows the
exact command, and waits for `confirmed-terminal` approval before
running it. The agent creates and checks out the branch. It does
not push.

### Step 2: Start the Story Orchestrator

Open Copilot Chat in Agent mode and select **Story Orchestrator**.
Provide the story ID, title, acceptance criteria, task list, target
modules, and constraints.

Example:

```text
Implement US-020: Document conversion and RustFS integration
supporting S4.

Acceptance criteria:
<paste the existing acceptance criteria>

Scope:
backend, RustFS integration, tests

Constraints:
Use the existing repository workflow. This project has no CI/CD
pipeline. Use local test evidence through scripts/preflight.ps1.
```

### Step 3: Approve Architecture

The Story Orchestrator delegates to the Story Architect. The
architect classifies the change, decides whether an ADR is required,
and identifies design constraints.

The agent pauses at Gate 1. Reply `approve`, `proceed`, or `yes`
only after you accept the architecture output.

### Step 4: Approve the Implementation Plan

After Gate 1 approval, the Story Orchestrator delegates to the
Story Planner. The planner produces a file-level implementation
plan, affected files, test strategy, assumptions, and risks.

The agent pauses at Gate 2. Reply `approve`, `proceed`, or `yes`
only after you accept the plan.

### Step 5: Let Development and QA Run

After Gate 2 approval, the Story Orchestrator delegates to the
Story Implementer. The implementer applies the approved plan.

The Story Orchestrator then delegates to Story QA and Review. QA
checks acceptance criteria, tests, regression risk, security risk,
and residual risks.

If QA is blocked, the Story Orchestrator routes back to the Story
Implementer for targeted rework. This loop repeats until blocking
findings are resolved or explicitly accepted as residual risk.

### Step 6: Read the Final Lifecycle Report

When QA passes, the Story Orchestrator writes a lifecycle report
under `.github/copilot-outputs/`. The report records the story
understanding, plan summary, implementation summary, QA findings,
final status, and residual risks.

### Step 7: Run Local Validation

This project has no CI/CD pipeline. Run the local pre-flight script
before commit preparation:

```text
Use scripts/preflight.ps1 to create test evidence for this branch.
```

The script writes:

```text
.github/copilot-outputs/<branch>-<tech>-test-evidence.md
```

The Commit Preparation skill, Azure DevOps PR Create skill, and
Pull Request Reviewer Agent consume this file.

### Step 8: Prepare the Commit

Use the **Commit Agent**. It loads the Commit Preparation skill,
checks staged files, checks forbidden files and secrets, checks
test evidence, proposes a commit message, and commits only after
approval.

Example:

```text
Use Commit Agent for US-020.
```

### Step 9: Push and Create the Pull Request

Push is always a separate approval. Ask Copilot to show the exact
push command before running it.

Then use the Azure DevOps PR Create skill or the
`azure-devops-pr` prompt:

```text
Create an Azure DevOps PR for this branch.
```

If test evidence is missing or failed, the pull request is created
as draft.

### Step 10: Review the Pull Request

The human reviewer uses the `review-pr` prompt, which invokes the
Pull Request Reviewer Agent.

Example:

```text
Review PR 1234.
```

The reviewer agent reads the pull request, writes a findings file,
posts comments only after per-comment approval, and votes only in a
separate user turn after the reviewer types the vote value back.

### Step 11: Merge

Merge is always performed by a human in Azure DevOps after the
required reviewers have approved. No agent merges or auto-completes
the pull request.

### Compact Flow

```text
Existing user story
  -> Branch Creator Agent
  -> Story Orchestrator
  -> Story Architect
  -> Gate 1 approval
  -> Story Planner
  -> Gate 2 approval
  -> Story Implementer
  -> Story QA and Review
  -> Rework loop if blocked
  -> Final lifecycle report
  -> scripts/preflight.ps1 test evidence
  -> Commit Agent
  -> push branch
  -> Azure DevOps PR Create skill
  -> Pull Request Reviewer Agent
  -> human merge
```

---

## Customizing coding conventions

Edit the relevant instruction files in `.github/instructions/`:

- `react-frontend.instructions.md` - adjust conventions for the React frontend
- `python-fastapi-backend.instructions.md` - adjust package structure, naming rules
- `devops-deployment.instructions.md` - update service names and ports
- `security.instructions.md` - add your security requirements

### 4. Update team ownership

Edit `.github/CODEOWNERS` to map modules to your teams:

```
/your-frontend/     @your-org/frontend-team
/your-backend/      @your-org/backend-team
/your-tests/        @your-org/qa-team
```

---

## Usage Examples

### Implementing a feature

```
Implement user story PROJ-123: Add user authentication to the login page
```

The agent will:
1. Analyze architectural impact (Phase 1)
2. Create an implementation plan (Phase 2)
3. Wait for your approval
4. Write code and tests (Phase 3)
5. Run QA validation (Phase 4)

### Fixing a bug

```
Fix the CORS configuration in the backend to allow the frontend origin
```

### Infrastructure change

```
Add a new volume to docker-compose.yml for persistent storage
```

### Writing tests

```
Create unit tests for the opportunities service
```

### Getting help

```
How does authentication work in this project?
```

---

## Agent Selection Logic

The Project Manager automatically routes requests based on keywords and file paths:

| Request contains | Routes to |
|---|---|
| React, component, frontend/, UI, screen | React Orchestrator |
| Python, FastAPI, backend/, endpoint, SQLAlchemy | Python FastAPI Orchestrator |
| Docker, deploy, infrastructure, Dockerfile | DevOps Orchestrator |
| script, bash, how to, explain | General Purpose Agent |

If the request is ambiguous, the agent will ask you to clarify.

---

## Approval Gates

At two points in the pipeline, the agent will pause and wait for your approval:

1. **After Architecture Phase**: Review the design decision before planning starts
2. **After Planning Phase**: Review the implementation plan before code is written

To approve, simply reply:
- `approve`
- `proceed`
- `yes`
- `go ahead`

To reject or request changes, describe what you want changed.

---

## Output Artifacts

Agents automatically create these files during execution:

- **ADRs**: `docs/architecture/decisions/ADR-NNN-<title>.md` (when required)
- **Implementation Plans**: `.github/copilot-outputs/<branch>-<tech>-planning-output.md`
- **QA Reports**: `.github/copilot-outputs/<branch>-<tech>-qa-output.md`

These provide a permanent record of decisions and can be referenced in pull requests.

---

## Customizing Agent Behavior

### Change an agent's personality

Edit the persona file in `.github/personas/PERSONA_<name>.md`. For example, to make the Java developer more strict about testing:

```markdown
## Testing Principles

- NEVER commit code without 100% line coverage
- ALWAYS write tests before implementation (TDD)
- Integration tests are mandatory for all REST endpoints
```

### Add a new technology stack

1. Create a new folder in `.github/agents/<technology>/`
2. Create orchestrator, architect, planner, implementer, and qa agents
3. Add routing rules to `project-manager.agent.md`
4. Create an instruction file in `.github/instructions/`

### Add a custom skill

Create a new folder in `.github/skills/<skill-name>/SKILL.md`:

```markdown
# Skill: Your Skill Name

## When to use

Describe when this skill should be loaded.

## Instructions

Step-by-step instructions for the agent to follow.
```

Register it in `copilot-instructions.md` under the Skills table.

---

## Troubleshooting

### Agent mode is not available
- Check that `chat.agent.enabled` is `true` in VS Code settings
- Update GitHub Copilot extensions to the latest version

### Agent doesn't follow instructions
- Check that the `.github` folder is in the project root
- Verify the `applyTo` pattern in instruction files matches your file paths
- Check if the agent is using the correct persona (shown at start of response)

### Git commands run unexpectedly
- This should never happen due to the safety rule in `copilot-instructions.md`
- If it does, report it as a bug in the agent configuration

### Agent creates files in wrong location
- Check `copilot-instructions.md` "Workspace Topology" section
- Verify the module paths match your actual project structure

---

## Best Practices

1. **Always start with Project Manager** - Don't try to invoke specific orchestrators directly
2. **Provide context** - Include story ID, module name, and acceptance criteria
3. **Review before approving** - Architecture and planning outputs are binding
4. **Keep instructions updated** - When conventions change, update instruction files
5. **Use symbolic links** - If managing multiple projects, symlink to a single `.github` source
6. **Version your ADRs** - Never delete or overwrite ADRs, always create new versions

---

## Security Notes

- **Never commit `.env`** - Environment files should be generated at deploy time
- Agents are configured to NEVER log credentials or run `git push` automatically
- All security rules are in `.github/instructions/security.instructions.md`

---

## Support and Contributions

This configuration is designed to be self-contained and forkable. You can:

- Use it as-is for projects matching the tech stack
- Adapt it by editing instruction files and agent routing
- Extend it by adding new agents and skills
- Share it with teams by providing this folder

For questions or issues, refer to the documentation in each agent file.

---

## Next Steps

1. ✅ Install the `.github` folder in your project
2. ✅ Enable agent mode in VS Code
3. ✅ Customize module names and routing in `copilot-instructions.md`
4. ✅ Update instruction files with your conventions
5. ✅ Test with a small feature request
6. ✅ Review and approve the architecture and plan
7. ✅ Watch the agent implement, test, and validate
8. ✅ Iterate based on your team's needs

Happy building! 🚀
