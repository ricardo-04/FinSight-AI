# Extraction Prompt

Extract structured financial metrics from the following document text.

Return a JSON object with:
- company (string)
- quarter (string, e.g. "Q1 2026")
- revenue (string)
- growth (string, YoY %)
- guidance (string)
- risks (array of strings)

Return ONLY valid JSON. No preamble, no markdown fences.
