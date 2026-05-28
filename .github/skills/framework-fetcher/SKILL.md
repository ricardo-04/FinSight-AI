---
name: framework-fetcher
description: >-
  Fetches the latest official documentation, release notes, or changelog for
  a framework or library before implementing version-specific features. Use
  this skill whenever an agent needs to verify current API signatures,
  deprecations, or breaking changes for React, FastAPI, SQLAlchemy, Vite,
   Keycloak, Alembic, Bootstrap, or React Router. Keywords: latest version,
  breaking changes, release notes, API reference, deprecation, changelog,
  upgrade.
---

# Framework Fetcher Skill

## Purpose

Before implementing work that depends on a specific framework or library
version, use this skill to verify that the implementation uses the current
stable API, not a deprecated or removed API.

This skill applies whenever any of the following conditions are met:
- The task involves a framework with rapidly changing APIs (React, FastAPI,
   SQLAlchemy, Vite, Keycloak) and depends on version-specific behavior.
- The codebase is being upgraded to a new major or minor version.
- A build failure, deprecation warning, or error suggests an API change.
- The agent has explicit evidence that an API changed between versions.
- The dependency-update skill flags a package as a possible breaking change.

Do not load this skill for ordinary feature work that follows established
local patterns and has no version uncertainty.

---

## Step-by-Step Instructions

### Step 1: Identify the Framework and Version

Before fetching documentation:
1. Read the relevant build file:
   - `pyproject.toml` for Python modules (look at `[project.dependencies]`)
   - `package.json` for React modules (look at `dependencies`)
2. Extract the exact version in use (e.g., `FastAPI 0.115.0`,
   `React 18.3.1`, `SQLAlchemy 2.0.32`).
3. If the version is a range, resolve it to the actual installed version
   by checking the lock file.

### Step 2: Fetch Official Release Documentation

Use the `fetch_webpage` tool to retrieve the official release notes or
migration guide. Use the following reference URLs as starting points:

| Technology | Documentation URL pattern |
|---|---|
| FastAPI | `https://github.com/tiangolo/fastapi/releases` |
| SQLAlchemy | `https://docs.sqlalchemy.org/en/20/changelog/` |
| Pydantic | `https://docs.pydantic.dev/latest/changelog/` |
| React | `https://react.dev/blog` |
| Vite | `https://github.com/vitejs/vite/releases` |
| Bootstrap | `https://github.com/twbs/bootstrap/releases` |
| Keycloak | `https://www.keycloak.org/docs/latest/release_notes/` |
| Alembic | `https://alembic.sqlalchemy.org/en/latest/changelog.html` |
| React Router | `https://github.com/remix-run/react-router/releases` |

If the exact version page is not reachable, fetch the closest available
version and note the discrepancy.

### Step 3: Extract Relevant Breaking Changes

From the fetched documentation, identify:
- Removed functions, classes, or configuration keys that the task uses.
- Renamed modules or dependencies.
- Changed function signatures or constructor options.
- New mandatory configuration requirements.
- Deprecated patterns that must be migrated.

Record these as a structured list:
```
## Breaking Changes for <Framework> <Version>
- <module>.<function>() removed - use <replacement> instead
- Configuration key `<old.key>` renamed to `<new.key>`
- ...
```

### Step 4: Verify Against Current Codebase

Use `grep_search` or `semantic_search` to check whether the codebase
currently uses any of the identified removed or deprecated APIs.

If deprecated usage is found:
- Flag it as a blocker if the feature being implemented depends on it.
- Flag it as a warning if it is in unrelated code.
- Do NOT silently implement new code around a deprecated API.

### Step 5: Document Findings

Before proceeding with implementation, record the findings:

```markdown
### Framework Version Check

- **Framework**: <name> <version>
- **Release notes fetched**: <yes/no>
- **Breaking changes affecting this task**: <list or "none">
- **Deprecated APIs in current codebase**: <list or "none">
- **Action required before implementation**: <list or "none">
```

---

## Output

After completing the framework fetch, produce a concise finding report and
attach it to the current phase output document in
`.github/copilot-outputs/`.

If no breaking changes are found, record:
```
Framework version check complete. No breaking changes affecting this task.
```

If breaking changes are found, halt implementation and present the
findings to the user before proceeding.
