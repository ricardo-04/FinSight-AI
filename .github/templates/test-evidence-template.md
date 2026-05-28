# Test Evidence Template

This template is the no-CI substitute for a build-validation status
check. The file lives under
`.github/copilot-outputs/<branch>-<tech>-test-evidence.md` and is
written by [scripts/preflight.ps1](../../scripts/preflight.ps1).

The Commit Preparation skill, the Azure DevOps PR Create skill,
and the Pull Request Reviewer Agent all read this file and refuse
or downgrade their actions when it is missing or its verdict is
not `Result: PASS`.

---

## Metadata

| Field | Value |
|---|---|
| Branch | `<branch>` |
| Technology | `<backend, frontend, devops, mixed>` |
| Story or task ID | `<JiraIssue> <UserStoryId>` |
| Date | `<YYYY-MM-DD HH:MM Z>` |
| Actor | `<UPN>` |

---

## Commands Executed

List every command and its exit code. Quote command lines exactly
as run.

| # | Command | Exit code |
|---|---|---|
| 1 | `<command>` | `<code>` |

---

## Output Summary

Paste the relevant tail of each command's output. Truncate to the
last 50 lines per command. Never paste secrets, tokens, or
credentials.

```text
<output excerpt>
```

---

## Coverage Summary

| Suite | Pass | Fail | Skipped | Coverage |
|---|---|---|---|---|
| `<suite>` | `<n>` | `<n>` | `<n>` | `<percent>` |

---

## Verdict

The verdict line is parsed by downstream skills and must be one of
the two values below, on a line by itself, with no trailing
characters.

```text
Result: PASS
```

or

```text
Result: FAIL
```

---

## Notes

- Required failures or known limitations.
- Stories with deliberately deferred coverage.
- Environment differences from production.
