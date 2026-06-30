---
name: workflow-bug-fix
description: Implementation workflow for fixing concrete software failures. Use when the user asks Codex to fix a bug, failing test, build error, runtime exception, regression, or broken behavior by reproducing the signal, diagnosing enough to change code, applying one targeted fix, and verifying the original failure.
---

# Workflow Bug Fix

## Routing Card
- role: primary
- intent_signature:
  - bug fix
  - failing test fix
  - build error fix
  - runtime exception fix
  - regression fix
  - 버그 고쳐
  - 테스트 실패 수정
- use_when:
  - the user asks to fix a concrete failure rather than only explain it.
  - a failing command, stack trace, broken behavior, or regression is available or can be captured.
  - implementation is expected after enough diagnosis.
- do_not_use_when:
  - the user asks only for root-cause analysis; use `analysis-bug`.
  - the same failure has repeated after one or more attempted fixes; use `workflow-recovery`.
  - the task is ordinary feature implementation with no current failure; use `workflow-implementation`.
  - the user asks only to design validation or rerun one known command.
- expected_inputs:
  - symptom, failing command, log, test output, stack trace, or broken behavior
  - expected behavior
  - relevant files or reproduction steps when available
- expected_outputs:
  - failure signal, active diagnosis, targeted code/test change, verification result, regression coverage note, and remaining uncertainty
- context_targets:
  must_read:
    - current failure signal or explicit `Unverified` gap
    - expected behavior
    - implicated source/test/config files when identifiable
  read_if_needed:
    - failing command output
    - call path and state/data flow around the failure
    - package manifests or environment config when implicated
    - repo validation contract
  do_not_load_by_default:
    - full repo
    - full memory bank
    - broad codebase report artifacts
    - unrelated historical failures
- risk_profile:
  reads:
    - failing output, targeted source, tests, config, and validation output
  writes:
    - WRITE_CODEBASE for one targeted bug-fix scope at a time
  tools:
    - CALL_PROCESS for reproduction, focused diagnostics, targeted tests, and validation
  sensitive_resources:
    - credentials default deny; external-service repro or destructive data repair requires explicit boundary review
- entry_scene:
  - PREPARE

## Purpose
- Own the normal fix loop for concrete software failures.
- Convert a failing signal into a targeted code/test change and verification.
- Escalate to `workflow-recovery` when normal fix iteration stops making progress.

## Activation
- Primary for "fix this bug", "make this failing test pass", "repair this build error", or "this regression is broken" requests.
- Attach `analysis-bug` when the cause is unclear enough that RCA discipline must lead before editing.
- Attach `workflow-validation` when installed or when the user explicitly asks for a validation matrix; otherwise use the local validation rules and mark deeper validation as `user_verification_needed`.
- Attach `workflow-rigor` for medium/high-risk fixes.

## Workflow
1. Lock the failure signal: command, observed behavior, expected behavior, and current reproducibility.
2. Create the fastest useful feedback loop: smallest test, command, fixture, route, or manual check.
3. Inspect the implicated call path and state/data flow before editing.
4. Choose one active diagnosis and one targeted fix.
5. Apply the fix with the smallest coherent diff.
6. Verify against the original failure signal.
7. Add or update regression coverage when feasible and connected to the failure.
8. If the same failure signature repeats after the targeted fix, hand off to `workflow-recovery`.

## Diagnosis Rules
- Gather enough evidence to justify the edit; do not require a full report when a narrow failure explains itself.
- Use `analysis-bug` when competing root-cause hypotheses remain broad or user asked for RCA.
- Do not present multiple vague suspects as the final cause of the fix.
- Do not hide the symptom with bypass branches, weaker assertions, broader mocks, or skipped tests.

## Fix Rules
- Fix the cause measured by the original signal, not just the easiest failing assertion.
- Change one causal area before revalidation unless the repo's existing pattern requires a paired test/source edit.
- Prefer a regression test at the seam where the bug was observable.
- If the correct fix requires a module-boundary change, attach `analysis-codebase-design` before broad refactoring.

## Output Contract
Return only the sections needed:
- `failure_signal`
- `feedback_loop`
- `diagnosis`
- `changed_artifacts`
- `verification`
- `regression_coverage`
- `remaining_uncertainty`
- `next_step`

## Cross-Skill Boundaries
- `analysis-bug` owns diagnosis-only RCA and broad root-cause selection.
- `workflow-recovery` owns repeated same-signature failure after attempted fixes.
- `workflow-implementation` owns ordinary feature work and refactoring without a current failure.
- `workflow-validation` owns validation-only planning or revised check selection when installed or explicitly requested.
- `analysis-codebase-design` owns deep module, seam, and boundary decisions when the fix needs structural change.

## Invocation Examples
Positive:
- "이 failing test 고쳐줘."
- "런타임 예외 원인 보고 수정까지 해줘."
- "이 regression 재현해서 코드 고쳐줘."

Negative:
- "왜 깨졌는지만 RCA 해줘." -> `analysis-bug`
- "새 기능 구현해줘." -> `workflow-implementation`
- "같은 테스트가 방금 수정 후에도 또 실패해." -> `workflow-recovery`
