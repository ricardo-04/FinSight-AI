---
applyTo: "**"
---

# Instructions - Style and Formatting

## Scope

These rules apply to all code, documentation, and agent outputs in the
repository. They ensure consistent formatting across all contributions.

---

## Character Rules

- Never use the em dash character (-). Use the hyphen instead.
- Never use ampersand in documentation. Write "and" in full.
- Never use emojis in code, commits, messages, or documentation.

---

## Naming Restrictions

Never use placeholder or meaningless variable names in production code:

`foo`, `bar`, `baz`, `temp`, `data`, `value`, `object`, `item`, `thing`,
`stuff`, `info`, `test`, `example`, `sample`, `dummy`, `placeholder`.

Choose descriptive names that communicate intent. Short names like `i`,
`j`, `k` are acceptable for loop indices and lambda parameters.

---

## Line Length

- JavaScript and JSX: maximum 100 characters per line.
- Python: maximum 79 characters per line (PEP 8).
- Markdown: maximum 72 characters per line for prose (code blocks exempt).

---

## Indentation

- JavaScript and JSX: 2 spaces.
- Python: 4 spaces.
- YAML: 2 spaces.
- Markdown: 2 spaces for nested lists.

---

## File Formatting

- All files must end with a single newline character.
- No trailing whitespace on any line.
- Use UTF-8 encoding for all text files.
