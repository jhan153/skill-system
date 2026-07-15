---
name: evaluation-harness
description: Review Skill System eval cases and observed behavior without mistaking routing, structure, mocks, or agent-authored expectations for user-visible semantic success.
---

# Evaluation Harness

## Routing Card
- role: primary
- intent_signature:
  - runtime usage eval, routing/negative case review, manual observation capture, or eval consistency
- use_when:
  - the user explicitly asks to inspect or improve eval cases, or capture observed skill behavior as usage-quality evidence.
- do_not_use_when:
  - release/readiness/package verdicts, ordinary implementation/validation, deployment/recovery, or invocation telemetry (`evaluation-usage-tracker`).
- expected_inputs:
  - targeted canonical eval cases, registry/routing context when relevant, and actual observation data when capture is requested
- expected_outputs:
  - scoped findings, condition-level evidence gaps, failure classification, and owner-mapped candidate changes; no readiness decision
- context_targets:
  must_read:
    - targeted eval cases and the supplied/observed result
  read_if_needed:
    - registry/routing, target skill or production owner, and field-feedback records for observed friction
  do_not_load_by_default:
    - live homes, plugin caches, sessions, raw transcripts, credentials, or unrelated eval families
- risk_profile:
  reads: scoped eval, routing, registry, skill, production-path, and redacted observation evidence
  writes: none unless explicitly requested; then canonical eval/routing/registry/skill files only
  tools: focused search and the narrow validator or fresh forward task that discriminates the finding
  sensitive_resources: deny credentials, raw prompts/transcripts, and private logs
- entry_scene:
  - PREPARE

## Evidence Authority
- An expected eval answer is a stated oracle, not an observation. Agent-authored cases/tests can preserve a regression expectation but do not independently discover or prove the user's contract.
- Record what each check covers: routing/context, structural, mock/interface, production runtime, semantic user outcome, or user-only judgment. A pass cannot cover a broader condition than its evidence.
- Mock success proves the mock boundary. Structural/harness/command success proves only its own contract. Missing, conflicting, `needs_review`, or unverified evidence remains unresolved rather than being averaged into success.
- Source selection, migration, media/data transformation, external-boundary, and adapter cases require actual production-path readback for semantic success. An adapter may translate formats; report source/policy/fallback ownership drift at the production owner.
- Eval findings are usage-quality evidence and improvement candidates, not release readiness, package validation, or critical signoff.

## Workflow
1. Select the smallest case set that discriminates the suspected behavior. State expected owner, material success condition, forbidden outcome, and acceptable evidence before judging the observation.
2. Observe a fresh request/dry run or use supplied behavior data. Record bundle/model/runtime identity when known; if observation is missing, list the missing fields and do not emit a dummy capture.
3. Compare routing, admitted context, output shape, production path, and material user outcome separately. Mark each condition pass/fail/needs review/unverified with its evidence scope and origin.
4. Classify the observed failure when applicable: routing miss, context overload, semantic mismatch, source-selection error, failure laundering, mock-only completion, or policy-owning adapter.
5. Map the fix to its real owner. Change an eval oracle only when the expectation was wrong; do not normalize a production bug by changing the case or hiding it behind an adapter.
6. Persist field-feedback YAML only for observed real-use friction and only when requested; redact user content. Synthetic cases stay eval cases, not field evidence.
7. If edits are requested, validate the changed YAML and run one focused fresh forward task when it can discriminate the finding. Report that evidence without upgrading it to readiness.

## Output Contract
Return only needed sections: case/success scope, observed behavior, condition evidence, failure class, owner-mapped changes, validation, and remaining gaps. A manual capture requires concrete case/date/evaluator/runtime, observed route/context/output, friction, follow-up, and one of `agent-verified`, `user-verification-needed`, or `unverified`; never output blank fields as observations.

## Cross-Skill Boundaries
- `evaluation-usage-tracker` owns metadata-only invocation count summaries.
- `report-critical` owns release/readiness/QA verdicts.
- `workflow-validation` owns validation plans for implementation changes.
- System `skill-creator` owns skill changes; `skill-system-repo-adapter` owns canonical integration/generation. `report-qualitative` owns formal reports.

## Validation
- Keep cases YAML-parseable and preserve exact observation provenance. One dry run may justify a case correction; maturity changes need repeated field feedback or one severe observed failure.
