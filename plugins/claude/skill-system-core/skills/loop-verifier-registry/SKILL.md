---
name: loop-verifier-registry
description: Map unclear loop success conditions to one schema-valid runtime verifier, scoped oracle/evidence, optional quality checks, and fail-closed unavailable behavior without executing them.
disable-model-invocation: true
---

# Loop Verifier Registry

## Routing Card
- role: support
- intent_signature:
  - loop verifier registry/map; success-condition evidence; 검증 조건 매핑
- use_when:
  - `plan-loop-term` or `workflow-loop-runner` needs an unclear verifier owner, command/path/check, evidence lane, or unavailable rule for one or more `SC-NNN` conditions.
- do_not_use_when:
  - execute the verifier, classify loop readiness, or run one obvious check local to the primary workflow.
- expected_inputs:
  - contract id and condition slice, target domain, material outcomes, known evidence paths, and current attestation boundary
- expected_outputs:
  - condition-keyed verifier companion with semantic scope/oracle, one runtime verifier, optional quality verifiers, receipt target, and success-blocking gaps
- context_targets:
  must_read:
    - accepted/draft contract identity and only the relevant success conditions
  read_if_needed:
    - `references/verifier-catalog.md`, cited plan/spec/oracle, or the narrow owner routing card for unfamiliar/cross-domain evidence
  do_not_load_by_default:
    - full repo/history, all design artifacts/logs, raw production data, or credentials
- risk_profile:
  reads: condition slice and narrow verifier/oracle context
  writes: none
  tools: none; mapping does not execute or attest a verifier
  sensitive_resources: credentials and live systems remain explicit approval gates
- entry_scene:
  - PREPARE

## Mapping Workflow
1. Keep `contract_id` and `SC-NNN`. Split a condition that combines independently failing material outcomes; do not create a second id namespace or give one condition multiple primary runtime verifiers.
2. In the planning companion, label evidence scope as `structural`, `runtime`, `semantic`, or `user-only`, and oracle origin as user decision, canonical source, external contract, formal invariant, observed production behavior, or agent-authored evidence. These are not new runtime-schema verifier types.
3. Assign exactly one owner and runtime type: `command_exit`, `artifact_exists`, `manual_check`, or `diff_scope`. Name its real command/path/check, evidence target, pass/fail signals, freshness, and unavailable behavior; otherwise keep the condition `unverified` or `blocked`.
4. Add a separate quality verifier only when it informs a visual, a11y, state, or review judgment that the runtime verifier cannot make. A report never replaces the condition's owned runtime receipt or user gate.
5. Match closure authority to the condition. `artifact_exists` closes only exact existence/digest; command exit closes only the commanded contract. Agent-authored tests cannot alone close a semantic rule they invented, and mocks prove only the mocked boundary. Source selection, migration, media/data transforms, external integration, and policy-owning adapters require an authoritative oracle plus representative actual-path readback.
6. Require canonical iteration-result receipts and preserve every conflicting or missing `fail`, `needs_review`, `unverified`, `blocked`, or `user-verification-needed` state. Free-form refs, maker self-report, easier proxies, or lower-scope passes cannot close it.

## Local V2 Ceiling
- Local v2 auto-passes only fresh exact `artifact_exists` evidence when exact existence/digest is the whole condition. `command_exit`, `manual_check`, and `diff_scope` stay open without host-authenticated production; unauthenticated manual events are procedural evidence, not user acceptance.
- An unavailable required verifier blocks success. Record one evidence-producing fallback when one exists; never substitute artifact presence or weaken the condition.

## Output Contract
Return a compact `verifier_map` keyed by `contract_id` and `SC-NNN`. For each condition include companion-only `evidence_scope` and `oracle_origin`; runtime `owner`, schema-valid `type`, evidence target, pass/fail signals; optional quality verifiers; independence; canonical receipt target; unavailable fallback/status/`blocks_success: true`; and only relevant anti-gaming signals or metrics. Do not emit a passing receipt or claim execution.

## Validation
- Every material condition has one primary verifier owner/type or an explicit success-blocking gap; quality checks remain separate.
- Closure evidence directly covers the stated condition and oracle, including actual-path readback where required.
- Local attestation ceiling, user gate, unresolved status, and maker/checker boundary remain intact.
- The mapping neither executed a verifier nor mutated files. Execution belongs to the verifier owner or `workflow-loop-runner`; readiness belongs to `loop-readiness-router`.
