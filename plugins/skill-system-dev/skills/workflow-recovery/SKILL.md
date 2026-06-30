---
name: workflow-recovery
description: Recovers repeated failure loops during implementation or validation. Use when the same test/build/runtime failure repeats, prior fixes did not resolve the issue, fake-fix risk is high, or the user asks to isolate one cause and break the retry loop.
---

# Workflow Recovery

## Routing Card
- role: primary
- intent_signature:
  - repeated failure loop
  - same test still failing
  - fake fix prevention
  - recovery mode
  - 범위 줄여서 원인 격리
  - 실패 루프 복구
- use_when:
  - the same failure has repeated after one or more attempted fixes.
  - validation keeps failing and the next step should isolate cause before more changes.
  - the user explicitly asks to stop fake fixes, reduce scope, or recover a stuck implementation.
  - an implementation workflow needs a recovery primary because normal execution is no longer making progress.
- do_not_use_when:
  - this is the first observation of a normal bug; use `analysis-bug` when root cause analysis is the main task.
  - the user asks for a broad redesign, plan package, or qualitative report.
  - the issue is solved and only final reporting or diff presentation remains.
  - the request is only to rerun a known command once.
- expected_inputs:
  - failing command, log, symptom, or validation output
  - latest attempted fix or changed files when available
  - success criterion and current blocker
- expected_outputs:
  - failure loop summary, narrowed repro, one active hypothesis, next diagnostic or fix, validation result, and rollback/fallback note
- context_targets:
  must_read:
    - current failure output or symptom
    - latest relevant diff or attempted fix summary
    - target test/build/runtime command when available
  read_if_needed:
    - implicated source files
    - recent validation output
    - active plan/spec only if it defines expected behavior
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated logs
    - broad historical transcripts
- risk_profile:
  reads:
    - failing output, latest diff, targeted source, and validation commands
  writes:
    - WRITE_CODEBASE only for one narrowed fix at a time after repro or hypothesis is locked
  tools:
    - CALL_PROCESS for repro, focused diagnostics, and targeted validation
  sensitive_resources:
    - credentials default deny; destructive recovery actions require explicit boundary review
- entry_scene:
  - PREPARE

## Purpose
- Break repeated failure loops without broad speculative fixes.
- Force one active hypothesis, one narrowed change, and one validation signal at a time.
- Preserve failed evidence instead of hiding it behind superficial patches.

## Activation
- Primary when the task has shifted from normal implementation to recovery from repeated failure.
- Attach `analysis-bug` when root-cause investigation needs deeper code reasoning.
- Attach `workflow-validation` when the recovery needs a new validation matrix.
- Attach `workflow-rigor` when the recovery fix is medium/high risk.

## Repeated Failure Threshold
Treat the task as a recovery loop when all are true:
- the same command, check, or user-observed behavior failed again
- the failure signature is the same or materially similar
- at least one attempted fix, rerun, or validation adjustment did not resolve it

Also activate immediately when the user explicitly asks to stop fake fixes, isolate one cause, or recover from a stuck loop.

## Workflow
1. Freeze the failure loop: record the failing command, symptom, and last attempted fix.
2. Reduce scope to the smallest reproducible signal.
3. Choose exactly one active hypothesis.
4. Run or propose the smallest diagnostic that can falsify that hypothesis.
5. Apply at most one targeted fix before revalidation.
6. Re-run the decisive check.
7. If the same failure repeats twice under this workflow, stop broadening and report the exact blocker.

## Diagnostic Examples
Choose one diagnostic at a time:
- test isolation: run the smallest failing test or test filter
- diff inspection: compare the latest attempted fix against the failure signature
- minimal reproduction: reduce input, fixture, route, or config to the smallest failing case
- dependency or version check: verify changed package/runtime/tool versions only when implicated
- environment check: verify missing files, env vars, services, permissions, or paths
- assertion/log review: confirm the failure signal still measures the intended behavior
- bisect-by-batch: isolate the last implementation batch that introduced the failure

## Anti-Fake-Fix Rules
- Do not weaken tests, assertions, validation criteria, or logs to hide failure.
- Do not add bypass branches without identifying the cause and risk.
- Do not stack multiple speculative fixes before revalidation.
- Do not call the issue fixed until the original failure signal is addressed.

## Capability Ceiling
- After evidence-changing recovery attempts, distinguish a procedure failure (fixable by narrowing, isolating, or changing one cause) from a capability ceiling (the model cannot produce the needed output: out-of-spec defect discovery, open-ended creative depth, or self-driven propagation beyond current evidence).
- When the blocker is a capability ceiling, do not add more retry or gate loops. Escalate instead — raise reasoning effort or model, or hand off to the user — and report `blocked` with the ceiling named, not as a procedure failure.

## Output Contract
Return only the sections needed:
- `failure_loop`
- `active_hypothesis`
- `diagnostic_or_fix`
- `validation_result`
- `rollback_or_fallback`
- `remaining_blocker`
- `next_recovery_action`

## Rollback And Fallback
- Roll back or isolate the latest targeted fix when it does not change the original failure signal and introduces new uncertainty.
- Keep the fix and continue only when validation shows the original failure moved or narrowed in a useful way.
- Fall back to diagnostic-only mode when the failing signal cannot be reproduced.
- Ask for user verification when the decisive check requires GUI, credentials, external services, or environment access outside the current boundary.
- Report `blocked` instead of patching when the only remaining actions would weaken tests, hide logs, or bypass assertions.

## Cross-Skill Boundaries
- `analysis-bug` owns broad RCA when no fix loop exists yet.
- `workflow-plan-runner` owns plan/spec-driven implementation order.
- `workflow-validation` owns check selection and validation-only execution.
- `report-critical` owns review verdicts, not recovery execution.

## Known Limits
- Recovery depends on having a real failing signal.
- If no reproducible signal exists, the next action is to capture one rather than patch blindly.
- This skill does not guarantee success; it prevents unbounded retry loops.

## Invocation Examples
Positive:
- "같은 테스트가 계속 실패해. fake fix 말고 원인 하나씩 격리하자."
- "방금 수정했는데 같은 build error가 또 나와. recovery mode로 보자."
- "테스트를 약화하지 말고 실패 신호부터 줄여줘."

Negative:
- "첫 실패 로그 한 줄 설명해줘." -> ordinary explanation
- "이 버그 원인 분석해줘." -> `analysis-bug` unless a fix loop already exists
- "이 테스트 하나만 다시 실행해줘." -> direct command, no recovery loop
