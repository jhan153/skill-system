---
name: workflow-validation
description: Select or run condition-matched validation for an existing change or plan, keeping claims within the authority and scope of the observed evidence.
disable-model-invocation: true
---

# Workflow Validation

## Routing Card
- role: execution_modifier
- intent_signature:
  - validation plan; verification matrix; validation-only execution; 검증 계획; 검증만
- use_when:
  - the user asks to validate an existing artifact/change, or an active workflow has non-obvious multi-surface or agent/user evidence choices.
- do_not_use_when:
  - implementation is the requested outcome; one obvious repository check suffices; or the request belongs to `evaluation-harness` or a critical verdict (`report-critical`).
- expected_inputs:
  - material success conditions, target artifact/change, oracle or expected result, risk boundary, and available observations
- expected_outputs:
  - condition-to-evidence mapping, scoped status, unresolved gaps, and one next evidence action
- context_targets:
  must_read:
    - validation request, material conditions, and changed artifact or relevant plan/spec slice
  read_if_needed:
    - oracle source, actual path, validation contract, scripts, CI, or boundary state
    - `workflow-recovery` when the same validation failure survives an intervention
  do_not_load_by_default:
    - full repo/memory, unrelated suites/evals, raw production data, or credentials
- risk_profile:
  reads: target, contract/oracle, actual path, and observed output
  writes: none unless explicitly requested
  tools: targeted non-destructive checks with a clear evidence purpose
  sensitive_resources: deny credentials; external or destructive checks require explicit boundary review
- entry_scene:
  - PREPARE

## Ownership And Workflow
- Implementation and ordinary focused checks stay with the primary owner. This modifier owns evidence selection only when validation is the task or the evidence choice is non-obvious.
1. List each material condition and classify it as `structural`, `runtime`, `semantic`, or `user-only`.
2. Bind its expected result to a user decision, canonical source, external contract, formal invariant, observed behavior, or agent-authored assumption.
3. Choose the smallest safe observation that can expose the realistic failure on the actual path; risk changes breadth, never evidence authority.
4. Record `pass`, `fail`, `needs_review`, `unverified`, or `blocked` for each condition without promotion.
5. When a material condition remains open, report one in-scope next observation if it already exists; otherwise mark `user_verification_needed` or `unverified` without proposing new test infrastructure.
6. When the same failure fingerprint survives an intervention, hand the stuck slice to `workflow-recovery`.

## Evidence Boundaries

| Evidence | Can establish | Cannot establish alone |
| --- | --- | --- |
| schema/static/build | declared structure or compilation | runtime/user semantics |
| agent-authored test | encoded assumption and regression memory | user/canonical authority |
| mock/fixture | behavior inside that boundary | production integration |
| runtime/readback | observed path and environment | unobserved scope or user judgment |
| user/external acceptance | accepted condition | unrelated conditions |

## Completion Gate
- A semantic condition needs a non-agent oracle plus evidence exercising its material path. A test may preserve an established oracle; it does not create one.
- Source selection, migration, media/data transforms, adapters, and external boundaries require actual selected/output readback. Missing or mismatched canonical input fails closed; verify that failing path itself before any happy-path rerun instead of bypassing it by supplying alternate input. A warning, placeholder, or silent legacy fallback is not resolution.
- Structural evidence is sufficient when the requested condition is exactly structural.
- A lower-scope pass never overrides conflicting or missing evidence. Required `fail`, `needs_review`, `unverified`, or `blocked` stays open until same-condition resolution/readback evidence exists.
- Missing GUI, credentials, external state, or user judgment remains `user_verification_needed` or `unverified`; passing checks imply release readiness only when the release gate binds those same conditions.
- A result-label gap is not implementation scope. Do not add tests, mocks, fixtures, dependencies, repeated unchanged runs, or a LoopRun solely to upgrade the label.

## Output Contract
Return only applicable fields: `validation_target`, condition/oracle/evidence/status mapping, `risk_boundary`, `checks_to_run`, `agent_verified`, `user_verification_needed`, `unverified_gaps`, and `next_validation_action`.
