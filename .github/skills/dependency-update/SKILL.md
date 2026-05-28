---
name: dependency-update
description: >-
  Guides agents through a safe dependency update cycle: identify
  outdated or vulnerable dependencies, propose version bumps, verify
  the build, and run Python and npm audit checks. Use this skill
  whenever a story involves dependency maintenance, CVE remediation,
  or version upgrades. Keywords: dependency update, CVE, vulnerability,
  npm audit, pip-audit, uv, version bump, upgrade.
---

# Dependency Update Skill

## Purpose

Dependency updates carry regression risk. This skill defines a safe,
repeatable process for updating Python uv-managed and npm dependencies
that preserves build stability, test coverage, and security compliance.

---

## Python - uv-managed Dependencies

### Step 0: Verify Tooling

```bash
cd backend
uv --version
```

If `uv` is not available, stop and report the missing prerequisite. Do
not fall back to unmanaged global pip commands.

### Step 1: Identify Outdated Dependencies

```bash
cd backend
uv sync --group dev
uv pip list --outdated
```

Focus on:
- Direct dependencies listed in `pyproject.toml`
- Dependencies flagged by `pip-audit` or another approved scanner
- Dependencies used in security-sensitive code paths (auth, crypto)

### Step 2: Run Security Audit

```bash
uvx pip-audit
```

Record every finding with severity HIGH or CRITICAL.

### Step 3: Propose Version Bumps

For each dependency to update, propose the change in `pyproject.toml`:
- Update the version constraint in `[project.dependencies]`
- Prefer the latest patch release within the current minor version
  unless a security fix requires a minor or major version jump
- Document the reason for each proposed bump

### Step 4: Apply Changes and Verify

After updating versions:

```bash
uv sync --group dev
uv run pytest
uvx pip-audit
```

Confirm:
- [ ] Install succeeds
- [ ] All unit tests pass
- [ ] `pip-audit` reports zero high or critical issues

---

## React Frontend - npm Dependencies

### Step 1: Identify Outdated Packages

```bash
cd frontend
npm outdated
```

Focus on packages with security advisories first, then semver minor
updates.

### Step 2: Run npm Audit

```bash
npm audit --audit-level=high
```

Record every `high` and `critical` finding.

### Step 3: Apply Safe Updates

For patch and minor updates without breaking changes:

```bash
npm update <package>
```

For major version updates, consult the package changelog first and use
the `framework-fetcher` skill to verify breaking changes.

### Step 4: Verify After Update

```bash
npm run build
npm audit --audit-level=high
```

Confirm:
- [ ] Build succeeds
- [ ] `npm audit --audit-level=high` reports zero high or critical issues
- [ ] Frontend tests are run if a test script exists; if no script is
  configured, record that limitation in the output artifact

---

## Output Format

Produce a dependency update report with:

1. **Scope:** modules updated
2. **Python changes:** table of package, old version, new version, reason
3. **npm changes:** table of package, old version, new version, reason
4. **CVEs remediated:** list with CVE ID, severity, affected package
5. **CVEs remaining:** list with justification for not remediating
6. **Build results:** pass/fail per module
