---
name: Defect Report
about: Report a defect found during development, testing or in production
title: "[DEFECT] "
labels: defect
assignees: ""
epic_link: SalesMate
---

## Reporter

**Name / Username:** <!-- Required: your name or GitHub username -->

## Description

A clear and concise description of the defect.

## Steps to Reproduce

1. Go to...
2. Do...
3. Observe...

## Expected Result

Describe what should happen.

## Actual Result

Describe what actually happens.

## Component (Required)

<!-- Select the affected component. At least one must be checked. -->

- [ ] backend (Python FastAPI)
- [ ] frontend (React)
- [ ] infra (Docker Compose, Keycloak)
- [ ] docs

## Detection Activity (Required)

<!-- Select the activity during which the defect was found. Select one only. -->

- [ ] Unit Test
- [ ] Integration Test
- [ ] System Test
- [ ] Acceptance Test
- [ ] Regression Test
- [ ] Exploratory Testing
- [ ] Performance Test
- [ ] Code Review
- [ ] Static Analysis
- [ ] Demo / Review
- [ ] Production / Live
- [ ] Customer Report

## Priority (Required)

<!-- Select one -->

- [ ] Blocker
- [ ] Critical
- [ ] High
- [ ] Medium
- [ ] Low

## Impact (Required)

<!-- Select one -->

- [ ] Blocker
- [ ] Critical
- [ ] Major
- [ ] Minor
- [ ] Trivial

## Affected Version (Required)

**Version / Branch:** <!-- Required: e.g. v1.2.0 or feature/SM-123-my-story -->

## Fix Version

**Target Version / Sprint:** <!-- Optional: to be filled by the triager -->

## Environment

- **Deployment environment:** (local / staging / production)
- **OS:**
- **Browser (if frontend):**

## Regression

- [ ] Yes
- [ ] No
- [ ] Unknown

## Root Cause

<!-- Optional: fill during investigation -->

## Workaround

<!-- Optional: describe any known workaround -->

## Logs and Evidence

Paste relevant log output, stack traces, or screenshots here.

```
[Paste logs here]
```

## Additional Context

Any other relevant context about the defect.
