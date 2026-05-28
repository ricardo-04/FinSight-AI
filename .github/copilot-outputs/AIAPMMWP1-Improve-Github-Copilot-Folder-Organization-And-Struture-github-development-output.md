# GitHub Workflow Customization Development Output

**Phase:** Development

## Changed Files

- `.github/git-commit-instructions.md`
- `.github/templates/PR_TEMPLATE.md`
- `.github/copilot-instructions.md`
- `.github/prompts/azure-devops-pr.prompt.md`
- `.github/prompts/azure-devops-commit.prompt.md`
- `.github/GETTING_STARTED.md`
- `.github/copilot-outputs/AIAPMMWP1-Improve-Github-Copilot-Folder-Organization-And-Struture-github-development-output.md`

## Commands Executed

No shell commands were executed.

Tool-based actions:
- Read repository governance and prompt template files.
- Delegated a read-only customization review to General Purpose Agent.
- Applied focused Markdown edits with the file patch tool.

## Results

Status: pass.

Implemented Azure DevOps branch, commit, pull request, target branch,
reviewer, and prompt workflow guidance for SalesMate.

Added a dedicated Azure DevOps commit prompt that removes the current
actor from the final pull request reviewer list before PR creation.

Added Azure CLI prerequisite notes to Azure DevOps prompts and Windows
plus WSL install guidance to the onboarding documentation.

Validation evidence:
- No forbidden ampersand or em dash characters found under `.github/`.
- No stale feature-prefix branch examples or legacy target branch examples
  remain in `.github/`.
- VS Code reported no diagnostics for the changed Markdown files.
- The Azure DevOps commit prompt frontmatter includes `name`,
  `description`, `argument-hint`, and `agent`.
- Azure DevOps prompt frontmatter uses the exact available agent name:
  `General Purpose Agent`.
- No prompt command example passes `caferreira@criticalsoftware.com` or an
  actor placeholder as an Azure DevOps reviewer.