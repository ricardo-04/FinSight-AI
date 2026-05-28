# .github - FinSight AI

This directory contains all GitHub Copilot customizations for the FinSight AI project.

## Structure

```
.github/
  copilot-instructions.md    - global Copilot behavior guidance
  constitution.md            - non-negotiable project rules
  git-commit-instructions.md - conventional commit format
  agents/
    project-manager.agent.md          - task routing entry point
    general-purpose.agent.md          - utility and infrastructure tasks
    story-orchestrator.agent.md       - cross-cutting story lifecycle
    story-architect.agent.md          - architecture assessment and ADR
    story-planner.agent.md            - implementation planning
    story-implementer.agent.md        - code and test implementation
    story-qa-review.agent.md          - QA review and release readiness
    backend/
      python-fastapi-orchestrator.agent.md
      python-fastapi-planner.agent.md
      python-fastapi-implementer.agent.md
      python-fastapi-qa.agent.md
    frontend/
      nextjs-orchestrator.agent.md
      nextjs-planner.agent.md
      nextjs-implementer.agent.md
      nextjs-qa.agent.md
  instructions/
    python-fastapi-backend.instructions.md  - backend conventions
    nextjs-frontend.instructions.md         - frontend conventions
    ai-rag.instructions.md                  - AI and RAG conventions
    devops-deployment.instructions.md       - Docker Compose conventions
    security.instructions.md               - OWASP security rules
    tests.instructions.md                  - testing conventions
    git-workflow.instructions.md           - branching and commit rules
  skills/
    confirmed-terminal/    - user-confirmation gate for shell commands
    commit-preparation/    - safe conventional commit workflow
  copilot-outputs/         - agent output logs (auto-generated)
```

## Quick Start

For any task, invoke the **Project Manager** agent - it will route your request to the correct domain agent.

For single-domain tasks, invoke the domain orchestrator directly:
- Backend work: **Python FastAPI Orchestrator**
- Frontend work: **Next.js Orchestrator**
- Cross-cutting: **Story Orchestrator**
- Infrastructure: **General Purpose Agent**
