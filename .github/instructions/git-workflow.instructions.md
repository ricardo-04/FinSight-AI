---
applyTo: "**"
---

# Instructions - Git Workflow

## Branch Naming

```
feature/<short-description>     - new features
fix/<short-description>         - bug fixes
refactor/<short-description>    - refactors without behavior change
docs/<short-description>        - documentation only
chore/<short-description>       - tooling, deps, config
```

Examples:
- `feature/rag-retrieval-threshold`
- `fix/extraction-agent-empty-response`
- `docs/architecture-overview`

## Commit Convention

Follow `.github/git-commit-instructions.md` for commit message format.

## Workflow

1. Branch from `main`.
2. Keep branches short-lived (single feature or fix).
3. Write tests before marking implementation complete.
4. Self-review your diff before requesting a review.
5. Squash fixup commits before merging.

## Rules

- Never commit directly to `main`.
- Never use `git push --force` on shared branches.
- Never bypass pre-commit hooks with `--no-verify`.
- All commits must be signed off if the project enforces DCO.
