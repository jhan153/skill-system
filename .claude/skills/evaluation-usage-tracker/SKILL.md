---
name: evaluation-usage-tracker
description: "Aggregate metadata-only skill invocation records into usage summaries and improvement candidates; complements evaluation-harness and field-feedback YAML records without storing raw prompts or transcripts."
---

# Evaluation Usage Tracker

## Routing Card
- role: primary
- intent_signature:
  - `usage tracking`
  - `호출 통계`
  - `사용량 요약`
  - `invocation metrics`
  - `usage summary`
  - metadata-only skill telemetry
- use_when:
  - the user wants invocation counts, low/high-use skills, over/under-trigger patterns, or maturity-upgrade candidates from a local metadata ledger.
  - the user asks for a no-data status for skill invocation logging.
  - summarized usage records, not raw prompts/transcripts, are available for aggregation.
- do_not_use_when:
  - the user wants release governance, readiness signoff, automatic maturity changes, or package validation.
  - the request requires reading raw prompts, transcripts, private logs, secrets, or full conversation text.
  - the user wants eval-case quality review rather than invocation counts; use `evaluation-harness`.
- expected_inputs:
  - local invocation ledger path or summarized usage records (metadata only)
  - optional skill registry or field-feedback YAML records for review context
- expected_outputs:
  - usage count summary, low/high-use skills, over/under-trigger candidates, suggested registry/eval updates, or no-data status
- context_targets:
  must_read:
    - local invocation ledger path or summarized records when available
  read_if_needed:
    - `skill_registry.md`
    - `field-feedback/*.yaml` records
    - `references/usage-summary-template.md` for output shape only
  do_not_load_by_default:
    - full repo
    - raw conversation transcripts
    - raw prompts
    - private logs
    - credentials
- risk_profile:
  reads:
    - READ_LOCAL_FS for private/local metadata ledger or sanitized summary records only
  writes:
    - WRITE_LOCAL_FS only for a requested usage summary; metadata only, never raw prompts
  tools:
    - local aggregation and focused search only
  sensitive_resources:
    - never store raw prompts, secrets, private logs, or full conversation text
- entry_scene:
  - PREPARE

## Related Skills
- `evaluation-harness`: reviews eval-case quality and manual observed-behavior captures.
- `field-feedback/*.yaml`: qualitative observation and correction records.
- `report-critical`: release/readiness/QA verdicts.

## Trigger Guard
Positive:
- `스킬 호출 통계 요약해줘`
- `usage tracking ledger 집계해줘`
- `low-use/high-use skill 후보 정리해줘`

Negative:
- Release governance, readiness scoring, or finality decisions.
- Raw prompt/transcript analysis.
- Eval-case review without invocation counts.

## Goal
Turn metadata-only invocation records into actionable, review-gated improvement candidates without exposing private prompts or transcripts.

## Ledger (metadata only)
Use this as a schema shape, not a blank output template.

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

- Raw usage logs stay private/local.
- The public bundle includes schema, summary template, and guidance only.
- If no metadata ledger exists, report no data and stop; do not invent metrics.

## Aggregation Workflow
1. Confirm a local invocation ledger path or summarized metadata records exist.
2. If no ledger/records exist, return the no-data output shape and stop.
3. Confirm the records are metadata-only; if a source contains raw prompts/transcripts/private logs, refuse that source rather than ingest it.
4. Aggregate counts by `primary_skill`, `family`, `trigger_type`, and `outcome`.
5. Separate over-trigger candidates from under-trigger candidates.
6. Cross-check candidates against field-feedback YAML records or eval cases when available.
7. Propose review-gated improvement candidates only; never change maturity automatically.

## Over/Under Trigger Rule
- A raw count alone never changes maturity or routing.
- Treat a skill as an improvement candidate only when counts combine with field feedback or an eval case showing a real over/under-trigger pattern.
- Low use may mean a missing alias/routing gap, not low value; flag for review rather than deprecation.
- High use may reflect a broad entry router rather than over-triggering; check outcomes before judging.

## Reference
- Read `references/usage-summary-template.md` for input ledger sample, output summary sample, redaction checklist, and no-data output shape.
- Read `references/harness-measurement-protocol.md` only when the user asks about harness gate measurement or holdout/sunset analysis.

## Output Contract
Return only the sections needed:
1. Usage count summary by skill and family
2. Low-use and high-use skills
3. Over/under-trigger candidates
4. Suggested registry/eval/skill-text updates, review-gated
5. Privacy/redaction status
6. No-data status when no metadata ledger exists

Do not output sample counts from the reference unless they are clearly labeled as examples.

## Resource and Risk Boundary
- Reads: local metadata ledger/summary only, plus selected registry/eval/field-feedback context when needed.
- Writes: local summary only; metadata-only; never raw prompts.
- Network/credentials: none.
- Destructive actions: none.

## Anti-Patterns
- Storing or analyzing raw prompts, secrets, transcripts, or private logs.
- Auto-changing maturity without human review.
- Treating counts as package readiness.
- Copying sample output numbers as if they were measured.
- Reporting no-data as failure when the ledger is intentionally private/local.

## Validation
- Confirm every input source is metadata-only before aggregation.
- Confirm no raw prompt, transcript, secret, private log, or full file content is copied into output.
- Confirm sample/template numbers are not mixed with measured counts.
- Confirm no-data output is used when no local ledger exists.

## Known Limits
- Counts are evidence, not verdicts; maturity changes still require review.
- Without a ledger, this skill reports there is no data rather than inventing metrics.
- Local invocation ledgers are intentionally private and may not be shipped in the bundle.
