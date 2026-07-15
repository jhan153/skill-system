---
name: evaluation-usage-tracker
description: Aggregate metadata-only skill invocation records into usage, outcome, and over/under-trigger summaries. Use when a local sanitized ledger or summary exists; never ingest raw prompts, transcripts, secrets, or private logs, and never convert counts directly into maturity or release decisions.
---

# Evaluation Usage Tracker

## Routing Card
- role: primary
- intent_signature: skill invocation metrics, usage summary, over/under-trigger telemetry, 호출 통계
- use_when: a local sanitized metadata ledger or summary can answer an invocation/outcome aggregation question
- do_not_use_when: eval-case review, release/readiness judgment, raw conversation analysis, or automatic maturity change is primary
- expected_inputs: selected sanitized source, field contract, scope, and time window
- expected_outputs: traceable counts/rates, routing candidates, privacy/no-data status, and review actions
- context_targets: read the selected source contract; load only candidate-specific registry/eval/feedback, the summary template for an artifact, or the measurement protocol for holdout/gate analysis
- risk_profile: metadata-only local aggregation; reject raw prompts, transcripts, secrets, identifiers, or private full-text logs
- entry_scene: PREPARE

## Input Gate
Accept only sanitized metadata fields such as time, skill IDs, request/trigger class, outcome, validation status, and explicit routing labels. If the named source is missing, unsafe, or unsuitable, return `no_data` or the privacy block and stop; never substitute templates, replay fixtures, repository inventory, or a stale ledger.

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
- `completed`, `agent-verified`, or another ledger label is an observed field value, not independent proof of semantic correctness or user success.
- Shared holdout arms or correlated interventions do not establish causal attribution.
- Structural ledger validity does not establish that the recorded classification was correct.

## Output
For one question, return the measured value with denominator, source/time window, and the limitation that changes its meaning. For an explicit artifact, use `references/usage-summary-template.md` and include only populated breakdowns, corroborated routing candidates, review actions, privacy/no-data status, and unresolved evidence gaps. Every number must trace to the selected source; recommendations remain candidates pending qualitative review.
