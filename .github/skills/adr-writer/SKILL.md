---
name: adr-writer
description: >-
  Produces Architecture Decision Records (ADRs) for significant changes.
  Use this skill whenever a change introduces a new integration pattern,
  external dependency, architectural boundary change, or breaking API.
  Keywords: ADR, architecture decision, design decision, module boundary,
  new service, new dependency, breaking change.
---

# ADR Writer Skill

## Purpose

An Architecture Decision Record (ADR) documents the context, decision,
alternatives considered, and consequences of a significant architectural
choice. This skill guides any agent through the process of recognizing
when an ADR is required and producing one correctly.

---

## Step 1: Determine Whether an ADR Is Required

An ADR is required when the change:
- Introduces a new external dependency (pip/uv, npm, Docker image)
- Introduces a new integration pattern not already used in the module
- Changes a public API (REST endpoint, S3 bucket schema)
- Adds, removes, or renames a module, service, or container
- Changes a module boundary or shared service API
- Introduces a new messaging pattern (sync vs. async, new protocol)
- Makes an irreversible or difficult-to-reverse infrastructure choice

If none of these apply, an ADR is not required. State this clearly and
proceed without producing one.

---

## Step 2: Gather Required Context

Before writing the ADR, collect:
1. The story ID and title from Jira
2. The specific problem being solved and why it requires a decision now
3. At least two alternatives that were considered, even if quickly
   dismissed
4. The selected approach and the primary reasoning

---

## Step 3: Check for Existing ADRs

Search `docs/architecture/decisions/` for existing ADRs that
may be related, superseded, or extended by this decision.

Name format: `ADR-NNN-short-title.md` where NNN is a zero-padded
sequential number.

Check the highest existing ADR number before assigning a new one.

---

## Step 4: Produce the ADR

Use `.github/templates/ADR_TEMPLATE.md` as the base. Fill every section:

- **Status:** Set to `Proposed`. The orchestrator or user sets it to
  `Accepted` when approved.
- **Context:** Explain the technical and organizational forces driving
  the decision.
- **Decision:** One or two sentences beginning with a verb. Must stand
  alone without the context section.
- **Alternatives Considered:** At least two. Explain why each was
  rejected.
- **Consequences:** List positive, negative, and neutral consequences
  explicitly. Do not leave sections empty.
- **Compliance:** Complete all four checkboxes.

---

## Step 5: Place the ADR

Save the ADR to `docs/architecture/decisions/`. Use the file
name format `ADR-NNN-short-title.md`.

Reference the ADR in:
- The implementation plan (link in the plan preamble)
- The copilot output log
- Any related feature specification document

---

## Failure Handling

If the context gathered is insufficient to fill the Decision or
Alternatives Considered sections, stop and ask the user explicitly for
the missing information. Do not produce an incomplete ADR.
