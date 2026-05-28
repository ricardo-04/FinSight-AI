# Structured Output Checklist

- [ ] Output is JSON-compatible or otherwise machine-validated.
- [ ] Required fields and optional fields are explicitly marked.
- [ ] Allowed values are listed for enums and workflow states.
- [ ] Source references are present when grounding is required.
- [ ] Failure categories are safe for orchestration decisions.
- [ ] Multilingual normalization is defined where required.
- [ ] No credentials, tokens, or unnecessary personal data are included.
- [ ] Downstream persistence and UI consumers are identified.
- [ ] Evaluation cases cover success, missing data, and invalid input.