---
name: evaluation-usage-tracker
description: Aggregate metadata-only skill invocation records into usage, outcome, and over/under-trigger summaries. Use when a local sanitized ledger or summary exists; never ingest raw prompts, transcripts, secrets, or private logs, and never convert counts directly into maturity or release decisions.
---

# Evaluation Usage Tracker

## Routing Card
- role: primary
- intent_signature:
  - skill invocation metrics, usage summary, over/under-trigger telemetry, 호출 통계
- use_when:
  - the user wants metadata-only invocation/outcome aggregation or an explicit no-data status.
- do_not_use_when:
  - the task is eval-case review (`evaluation-harness`), release/readiness verdict, raw conversation analysis, or automatic maturity change.
- expected_inputs:
  - local sanitized ledger path or summarized records
- expected_outputs:
  - measured usage/outcome summary, evidence-backed routing candidates, privacy status, or no-data result
- context_targets:
  must_read:
    - requested ledger/summary source and its field contract
  read_if_needed:
    - selected registry/eval/field-feedback records needed to test a candidate
    - `references/usage-summary-template.md` for an explicit artifact shape
    - `references/harness-measurement-protocol.md` only for holdout/gate measurement
  do_not_load_by_default:
    - full repo, raw prompts/transcripts, private logs, or unrelated feedback
- risk_profile:
  reads:
    - sanitized metadata records only
  writes:
    - requested metadata-only summary; no raw content
  tools:
    - local aggregation and focused lookup
  sensitive_resources:
    - reject sources containing raw prompts, transcripts, secrets, or private full-text logs
- entry_scene:
  - PREPARE

## Input Gate
Accept records containing only fields such as timestamp, primary/supporting skill IDs, family, trigger type, request class, outcome, validation status, and explicit over/under-trigger labels. Free-text notes must already be sanitized.

If no suitable ledger exists, report `no_data` and stop. Do not copy sample values from a template or infer counts from repository files.

## Workflow
1. Verify source location, scope, time window, and metadata-only status.
2. Aggregate by skill, family, trigger type, outcome, and validation status.
3. Distinguish observed counts from rates; state the denominator and missing/unknown records.
4. Identify candidate over/under-trigger patterns from outcomes and explicit labels.
5. Cross-check a candidate against field feedback or a routing eval when available.
6. Recommend the smallest review-gated registry/eval/skill-text change; never mutate maturity automatically.

## Interpretation Rules
- Low use may mean a narrow valuable skill, missing alias, no exposure, or missing telemetry.
- High use may be expected for an entry router; inspect outcome/reroute rates before calling it over-triggering.
- Counts without exposure/denominator data do not establish selection quality.
- Shared holdout arms or correlated interventions do not establish causal attribution.
- Structural ledger validity does not establish that the recorded classification was correct.

## Output
For one question, return the measured number and its denominator/source limitation directly. For an explicit summary artifact, include usage/outcome breakdown, low/high-use observations, over/under-trigger candidates with corroborating evidence, recommended review actions, privacy status, and no-data gaps. Omit empty sections.

## Behavior Cases
- Positive: “이 sanitized invocation ledger에서 reroute율과 under-trigger 후보를 집계해줘.”
- Negative: “원문 대화를 읽고 어떤 스킬이 맞았는지 분석해줘.” → reject raw transcript ingestion.
- Edge: no exposure denominator exists → report counts only; do not call a low count an under-trigger rate.

## Validation
- Every number traces to the selected source and time window.
- Sample/template data are excluded from measured results.
- Raw private text is absent from input and output.
- Recommendations remain candidates pending qualitative review.
