# Usage Summary Template

These examples show shape only. Do not copy the sample counts, dates, or skill
names into a real usage summary unless the local metadata ledger actually
contains those values.

## Input ledger sample (metadata only)
```yaml
- timestamp: 2026-06-15T10:00:00Z
  primary_skill: analysis-bug
  supporting_skills: [workflow-validation]
  family: analysis
  trigger_type: explicit
  request_class: bug_diagnosis
  outcome: completed
  validation_status: agent-verified
  over_triggered: []
  under_triggered: []
  notes: ""
```

## Output summary sample
```markdown
usage summary (n=120 invocations, 2026-06-01..06-15)
- by family: analysis 38, design 22, report 18, workflow 15, memory 12, research 9, others 6
- high-use: analysis-bug (21), design-frontend (14)
- low/zero-use: search-router (0), evaluation-usage-tracker (1), plan-long-term-package (0)
- over-trigger candidates: report-qualitative (6 rerouted to report-critical)
- under-trigger candidates: search-router (evidence requests went straight to research-router)
- review-gated suggestions: add search-router negative-routing examples; revisit report-qualitative vs report-critical guard
```

## Redaction checklist
- [ ] no raw prompts or transcript text
- [ ] no secrets, tokens, credentials, file contents
- [ ] only skill IDs, family, trigger_type, outcome, validation_status, labels, brief sanitized notes

## No-data output
```markdown
usage summary
- status: no data
- reason: no local invocation ledger found (metadata ledger is private/local and not shipped in the bundle)
- next: enable local invocation logging, then re-run
```
