---
name: evaluation-usage-tracker
description: "Aggregate metadata-only skill invocation records into usage summaries and improvement candidates; complements evaluation-harness and FIELD_FEEDBACK without storing raw prompts or transcripts."
---

# Evaluation Usage Tracker

## Routing Card
- role: support
- intent_signature:
  - `usage tracking`, `호출 통계`, `invocation metrics`, `usage summary`
- use_when:
  - the user wants invocation counts, low/high-use skills, over/under-trigger patterns, or maturity-upgrade candidates from a local ledger.
- do_not_use_when:
  - package approval, readiness signoff, automatic maturity changes, or analysis of raw prompts/transcripts.
  - no local invocation ledger or summarized records exist.
- expected_inputs:
  - local invocation ledger or summarized usage records (metadata only)
- expected_outputs:
  - usage count summary, low/high-use skills, over/under-trigger candidates, suggested registry/eval updates
- context_targets:
  must_read:
    - the local invocation ledger or summary records
  read_if_needed:
    - `skill_registry.md` and `FIELD_FEEDBACK.md` for context
  do_not_load_by_default:
    - full repo
    - raw conversation transcripts
- risk_profile:
  reads:
    - READ_LOCAL_FS for the private/local invocation ledger
  writes:
    - WRITE_LOCAL_FS only for a requested usage summary; metadata only, never raw prompts
  tools:
    - none beyond local aggregation
  sensitive_resources:
    - never store raw prompts, secrets, private logs, or full conversation text
- entry_scene:
  - PREPARE

## Related Skills
- `evaluation-harness`: reviews runtime usage eval-case quality (qualitative cases).
- `FIELD_FEEDBACK.md`: qualitative observation and correction notes.

## Trigger
- `usage tracking`, `호출 통계`, `사용량 요약`, `invocation metrics`

## Trigger Guard (Do Not Trigger)
- Package approval, readiness scoring, or finality decisions.
- Any request that would require reading raw user prompts or transcripts.

## Goal
- Turn metadata-only invocation records into actionable, review-gated improvement candidates.

## Ledger (metadata only)
```yaml
timestamp:
primary_skill:
supporting_skills:
family:
trigger_type: explicit | implicit | router | support
request_class:
outcome: completed | blocked | rerouted | skipped
validation_status:
over_triggered: []
under_triggered: []
notes:
```
- Raw usage logs stay private/local. The public bundle includes schema, summary template, and guidance only.

## Aggregation Workflow
1. Confirm a local invocation ledger (or summarized records) exists; if not, report "no data" and stop.
2. Confirm the records are metadata-only; if a source contains raw prompts/transcripts, refuse that source rather than ingest it.
3. Aggregate counts by `primary_skill`, `family`, `trigger_type`, and `outcome`.
4. Separate over-trigger candidates (frequent `rerouted`/`skipped` or wrong-family hits) from under-trigger candidates (near-zero use).
5. Propose review-gated improvement candidates only; never change maturity automatically.

## Over/Under Trigger Rule
- A raw count alone never changes maturity or routing.
- Treat a skill as an improvement candidate only when counts combine with field feedback or an eval case showing a real over/under-trigger pattern.
- Low use may mean a missing alias/routing gap, not low value; flag for review rather than deprecation.

## Reference
- Read `references/usage-summary-template.md` for an input ledger sample, output summary sample, redaction checklist, and the no-data output shape.

## Output Contract
1. Usage count summary (by skill and family)
2. Low-use and high-use skills
3. Over/under-trigger candidates
4. Suggested registry/eval updates (review-gated)

## Resource and Risk Boundary
- Reads: local ledger/summary only.
- Writes: local summary only; metadata-only; never raw prompts.
- Network/credentials: none.
- Destructive actions: none.

## Anti-Patterns
- Storing or analyzing raw prompts, secrets, or transcripts.
- Auto-changing maturity without human review.
- Treating counts as package readiness.

## Known Limits
- Counts are evidence, not verdicts; maturity changes still require review.
- Without a ledger, this skill reports there is no data rather than inventing metrics.
