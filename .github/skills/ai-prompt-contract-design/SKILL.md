---
name: ai-prompt-contract-design
description: >-
  Designs structured runtime AI prompt contracts for SalesMate
  classification, analysis extraction, proposal generation, effort
  estimates, requirement traceability, Mermaid diagrams, and RAG answers.
  Use this skill when defining prompt inputs, output schemas, validation,
  failure handling, grounding, or source references. Keywords: prompt
  contract, structured output, AI workflow, prompt design, RAG, Mermaid,
  traceability, proposal generation.
---

# AI Prompt Contract Design Skill

## Purpose

SalesMate runtime AI workflows create persisted data, proposal artifacts,
and user-visible analysis. This skill defines prompt contracts before
runtime prompts are implemented so outputs are typed, validated,
traceable, and usable by deterministic application code.

Do not confuse runtime product prompts with Copilot Chat prompt files.
Use `.github/templates/prompt_template.md` only when creating a Copilot
Chat prompt file for the development workflow.

---

## Step 1: Identify The Runtime Workflow

Capture the workflow and story context:
- Story ID and title.
- Screen or service affected, such as S3, S4.2, S4.4, or S4.5.
- Trigger, such as scheduled classification, analysis extraction,
  proposal generation, or chat answer generation.
- Downstream consumer, such as persistence models, proposal assembly,
  UI tabs, CSV export, Mermaid rendering, or RAG source display.

---

## Step 2: Gather Domain Inputs

Read only the evidence needed for the contract:
- `docs/user-stories.csv` for acceptance criteria.
- `docs/functional-description.md` for domain workflow details.
- `docs/requirements.md` for security, traceability, and validation
  requirements.
- Current backend models, services, and API schemas when implementation
  already exists.

Do not invent unavailable source fields. Mark them as required upstream
inputs or open questions.

---

## Step 3: Define Inputs And Constraints

For each prompt workflow, specify:
- Input sources, such as normalized document chunks, manual instructions,
  proposal templates, analysis outputs, or latest proposal versions.
- Required language normalization, including multilingual tender input
  and English output requirements.
- Authorization and scope constraints, especially opportunity scope,
  cluster scope, and user role.
- Token, size, and retrieval limits.
- Data that must not be logged or exposed.

---

## Step 4: Define The Output Contract

Use `.github/skills/ai-prompt-contract-design/templates/prompt-contract-template.md`
as the contract template.

Each output contract must include:
- Field names, types, required flags, and allowed values.
- Stable identifiers for requirements, risks, activities, and sources.
- Confidence or rationale fields only when the product needs them.
- Source references or snippets when the UI or RAG answer needs grounding.
- Failure categories that orchestration can route safely.
- Persistence and proposal assembly expectations.

Prefer JSON-compatible structures for runtime outputs. Avoid free-form
text where downstream code needs deterministic assembly.

---

## Step 5: Define Validation And Evaluation

Use `.github/skills/ai-prompt-contract-design/checklists/structured-output-checklist.md`
before implementation.

Define at least:
- Schema validation rules.
- Required field validation and allowed value checks.
- Hallucination controls and source-reference checks.
- Golden-path and failure-path evaluation cases.
- Multilingual input case when the story includes tender classification
  or analysis extraction.

---

## Step 6: Decide The Artifact Type

Choose the correct artifact:
- Runtime prompt contract: documentation or application prompt asset used
  by backend services.
- Copilot Chat prompt file: `.github/prompts/*.prompt.md`, only for
  development workflow automation.
- Repository instruction: always-on rules for all agents.
- Test fixture: evaluation sample used by automated or manual checks.

If a runtime application prompt file location is not established, propose
the location and ask before creating it.

---

## Output Format

Produce an AI prompt contract report with:

1. **Workflow:** story, trigger, consumer, and owner layer.
2. **Inputs:** source fields, constraints, and missing upstream data.
3. **Output schema:** fields, types, allowed values, and examples.
4. **Validation:** schema checks, source checks, and failure categories.
5. **Evaluation:** golden cases, failure cases, and multilingual cases.
6. **Implementation notes:** where the prompt contract should live.
