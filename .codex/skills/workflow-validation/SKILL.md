---
name: workflow-validation
description: Design or run focused validation for planned or completed changes. Use for validation strategy, check selection, verification matrices, or validation-only execution; support implementation only when evidence selection is non-obvious.
---

# Workflow Validation

## Routing Card
- role: execution_modifier
- intent_signature:
  - validation plan
  - verification matrix
  - smoke test selection
  - 검증 계획
  - 검증만
  - 테스트/스모크/수동확인 매트릭스
- use_when:
  - the user asks how to validate, or to validate an already changed artifact.
  - an active workflow has non-obvious, multi-surface, or agent/manual evidence choices.
- do_not_use_when:
  - the user asks to implement rather than validate.
  - the request is usage eval (`evaluation-harness`) or a critical verdict (`report-critical`).
  - one obvious check or normal repository validation already suffices.
- expected_inputs:
  - target artifact/change, success criteria, risk boundary, and available checks
- expected_outputs:
  - condition-to-evidence matrix, oracle authority, status, and unverified gaps
- context_targets:
  must_read:
    - current validation request
    - changed artifact or plan/spec slice under validation
  read_if_needed:
    - validation contract, package scripts, CI config, or referenced plan/spec
  do_not_load_by_default:
    - full repo, memory, unrelated suites, or unrelated eval cases
- risk_profile:
  reads:
    - target artifact, contract, and observed output
  writes:
    - none unless explicitly requested
  tools:
    - CALL_PROCESS for targeted non-destructive checks when command purpose is clear
  sensitive_resources:
    - credentials default deny; external systems and destructive checks require explicit boundary review
- entry_scene:
  - PREPARE

## Contract
- Validate the requested success condition, not the existence of a command or test.
- Keep implementation ownership with the primary workflow. This skill selects evidence and prevents claims from exceeding its scope.
- In normal implementation, ordinary focused checks stay with the primary owner.
- Risk tier controls check breadth, not evidence authority.

## Workflow
1. List the material success conditions and classify each as `structural`, `runtime`, `semantic`, or `user-only`.
2. Bind the expected result to its oracle: user decision, canonical source, external contract, formal invariant, observed behavior, or agent-authored assumption.
3. Choose the smallest check that can expose the realistic failure on the actual path; run it only when safe.
4. Record `pass`, `fail`, `needs_review`, `unverified`, and `blocked` per condition without promotion.
5. Report exactly one next evidence-producing action when a material condition remains open.

## Evidence Authority

| Evidence | Can establish | Cannot establish alone |
| --- | --- | --- |
| schema/static/build | declared structure or compilation | runtime or user-visible semantics |
| agent-authored test | the encoded assumption and regression memory | that the assumption is the user/canonical contract |
| mock/fixture | behavior inside the mocked boundary | the production integration path |
| runtime/readback | the observed path in that environment | unobserved environments or user-only judgment |
| user/external acceptance | the accepted scope | unrelated conditions |

- A semantic condition needs a non-agent oracle and evidence that exercises its material path. Tests may carry that oracle after it is established; they do not create it.
- Source selection, migrations, media/data transforms, adapters, and external boundaries require actual-path readback. Confirm the selected output and fail-closed missing-source behavior; a placeholder or warning is not resolution unless the user contract accepts it.
- Structural evidence is sufficient when the requested condition is genuinely structural, such as validating one schema artifact.

## Risk-Tier Check Sets
- Low: one decisive condition-matched check.
- Medium: direct-path check plus the smallest material regression check.
- High: direct-path/readback evidence plus relevant rollback, fallback-failure, or user/external observation.

Do not use risk tier to inflate validation. Pick the narrowest set that can detect the realistic failure mode.

## Completion Gate
- A lower-scope pass never overrides conflicting or missing evidence. Mock success proves only the mock; command exit proves only the command's contract.
- Required `fail`, `needs_review`, `unverified`, or `blocked` stays open until resolution/readback evidence addresses that same condition.
- Missing GUI, credentials, external state, or user judgment remains `user_verification_needed` or `unverified`.
- Passing checks do not imply release readiness unless the release gate explicitly binds the same conditions.

## Output Contract
Return only applicable fields: `validation_target`, `risk_boundary`, `risk_tier`, `checks_to_run`, `agent_verified`, `user_verification_needed`, `unverified_gaps`, `next_validation_action`.
