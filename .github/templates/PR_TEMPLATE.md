# Pull Request: [JIRA-ID] [US-ID] [Short Description]

**Story/Task:** [JIRA-ID] [US-ID]
**Branch:** `feature/[JIRA-ID]-[US-ID]-[Title-With-Proper-Casing]`
**Target Branch:** `master`
**Module(s):** [e.g., backend, frontend, infra]
**Type:** Feature / Bug Fix / Refactor / Documentation / Infrastructure

**Reviewers:**
- `ra-pombo@criticalsoftware.com`
- `pmfmonteiro@criticalsoftware.com`
- `dsmendes@criticalsoftware.com`

---

## Summary

Describe what this PR does in two or three sentences. Explain the change
and why it is needed.

---

## Changes

List the main changes grouped by file or concern:

- `path/to/file.py`: Short description of change
- `path/to/Component.jsx`: Short description of change

---

## Test Evidence

- [ ] Unit tests pass when configured
- [ ] Lint passes if lint tooling is configured
- [ ] Coverage is reported if coverage tooling is configured
- [ ] No regressions in existing tests
- [ ] Tests pass (if applicable)

Paste relevant test output or coverage summary here:

```
[Test output]
```

---

## Security Checklist

- [ ] No credentials, tokens, or key material in source code
- [ ] All network sockets use TLS 1.2 or higher
- [ ] All inputs at system boundaries are validated
- [ ] No sensitive data logged
- [ ] OWASP Top 10 compliance verified

---

## Documentation

- [ ] README updated
- [ ] Architecture docs updated
- [ ] Configuration guides updated
- [ ] Inline comments added where intent is not obvious
- [ ] ADR created (if architectural decision was made)

---

## Reviewer Notes

Add any context that would help the reviewer: edge cases, trade-offs,
follow-up tasks, or known limitations.
