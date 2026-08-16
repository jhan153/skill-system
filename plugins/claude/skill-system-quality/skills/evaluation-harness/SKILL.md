---
name: evaluation-harness
description: Review existing Skill System eval cases for syntax, internal consistency, and scoped regression intent when explicitly requested. Never use scenario results as field-quality evidence or collect user conversations.
disable-model-invocation: true
---

# Evaluation Harness

## Routing Card
- role: primary
- intent_signature:
  - existing eval-case review, schema consistency, or regression-oracle maintenance
- use_when:
  - the user explicitly asks to inspect or repair existing Skill System eval cases
- do_not_use_when:
  - ordinary implementation, field feedback, release/readiness work, invocation telemetry, synthetic quality scoring, or new scenario generation is primary
- expected_inputs:
  - targeted canonical eval cases and the contract they are intended to preserve
- expected_outputs:
  - scoped structural findings and narrowly owned case corrections; no field-quality or readiness verdict
- context_targets:
  must_read:
    - targeted existing eval cases
  read_if_needed:
    - the referenced routing, skill, or schema owner
  do_not_load_by_default:
    - live homes, plugin caches, sessions, prompts, transcripts, user identifiers, or unrelated eval families
- risk_profile:
  reads: scoped eval, routing, skill, and schema files
  writes: none unless explicitly requested; then only the targeted canonical eval or directly owning source
  tools: focused search and the narrow existing syntax/schema validator
  sensitive_resources: deny prompts, transcripts, private logs, credentials, and automatic usage records
- entry_scene:
  - PREPARE

## Evidence Authority
- An expected eval answer is an authored oracle, not an observation of user-visible quality.
- YAML/schema validity proves only structural consistency.
- Scenario passes cannot establish field success, release readiness, skill quality, or user satisfaction.
- Field-driven improvements start only from a problem the user explicitly reports in conversation; this skill does not collect or persist that conversation.

## Workflow
1. Select only the existing cases named by the user or directly implicated by the requested consistency problem.
2. Compare each case with its current routing, skill, or schema owner.
3. Correct an oracle only when the owner contract changed or the case is internally inconsistent; never rewrite a case to hide a product or harness failure.
4. If edits are requested, run the narrow existing YAML/schema validator for the changed files.
5. Report the exact structural contract covered and state that no field-quality conclusion follows.

## Output Contract
Return only the affected cases, the concrete inconsistency, the owning source, any narrow correction, and the validator result. Do not emit readiness, user-quality, telemetry, or field-evidence judgments.

## Cross-Skill Boundaries
- `report-critical` owns release/readiness/QA verdicts.
- `workflow-validation` owns validation selection for implementation changes.
- Canonical integration and generated-target maintenance stay with the current repository implementation owner.

## Validation
Keep edited cases YAML-parseable and schema-valid. Do not create fresh conversational scenarios, forward tasks, user records, or new validation infrastructure.
