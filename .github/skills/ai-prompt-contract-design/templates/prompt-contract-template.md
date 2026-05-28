# Prompt Contract Template

## Contract Metadata

| Field | Value |
|---|---|
| Contract name | `<name>` |
| Story ID | `<US-000>` |
| Runtime workflow | `<classification, analysis, proposal, RAG>` |
| Consumer | `<service, screen, artifact>` |
| Status | Planned |

## Purpose

Describe the business decision or artifact this prompt supports.

## Inputs

| Input | Source | Required | Constraints |
|---|---|---|---|
| `<input>` | `<source>` | Yes | `<limits>` |

## Output Schema

```json
{
  "fieldName": "string"
}
```

## Validation Rules

- Required fields:
- Allowed values:
- Source-reference rules:
- Failure categories:

## Persistence And Consumers

- Persistence target:
- API response fields:
- UI or artifact consumer:

## Evaluation Cases

| Case | Purpose | Expected result |
|---|---|---|
| Golden path | Valid input | Valid structured output |
| Missing data | Required input absent | Recoverable failure |

## Open Questions

- `<question>`
