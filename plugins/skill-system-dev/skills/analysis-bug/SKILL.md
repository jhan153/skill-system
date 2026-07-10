---
name: analysis-bug
description: Diagnose recurring, unclear, or high-risk software failures by locking the repro, testing competing causes, and selecting one evidence-backed root cause. Use for RCA or when diagnosis must precede a fix; use workflow-bug-fix when the primary request is to repair a concrete failure directly.
---

# Analysis Bug

## Routing Card
- role: primary
- intent_signature:
  - root-cause analysis, deep debugging, recurring or unclear failure, 원인 분석
- use_when:
  - the user asks why a failure occurs or explicitly requests RCA.
  - competing causes must be discriminated before a safe edit is possible.
- do_not_use_when:
  - the primary request is to fix a concrete failing test/build/runtime signal; use `workflow-bug-fix`.
  - the approach is known and no causal uncertainty remains.
  - the question is algorithm selection, architecture design, or broad repository reporting.
- expected_inputs:
  - observed symptom, expected behavior, triggering condition, and available evidence
- expected_outputs:
  - repro status, decisive evidence, primary root cause, fix direction, and verification target
- context_targets:
  must_read:
    - symptom and expected behavior
    - repro steps or an explicit `Unverified` gap
  read_if_needed:
    - implicated source/tests, logs, call path, state/data flow, timing, and environment
  do_not_load_by_default:
    - full repo, full memory bank, unrelated historical failures, or codebase-wide reports
- risk_profile:
  reads:
    - targeted code, tests, logs, configs, and repro evidence
  writes:
    - none in diagnosis-only work; code only when the user explicitly requested RCA plus implementation
  tools:
    - focused repro, diagnostic, and validation commands
  sensitive_resources:
    - credentials default deny; redact external-service and production evidence
- entry_scene:
  - PREPARE

## Causal Diagnosis Loop
1. Lock the contract: observed behavior, triggering condition, expected result, and reproducibility.
2. Trace the smallest relevant end-to-end path across call flow, state/data flow, and timing/environment.
3. When the cause is not already decisive, keep two or three competing hypotheses temporarily.
4. Run the cheapest observation that produces different predictions for those hypotheses.
5. Record disconfirming evidence as well as confirming evidence.
6. Select one primary root cause. Keep secondary factors only when they change the repair or recurrence risk.
7. Define the fix direction and the check that reproduces the original signal.

Static inspection can establish possible paths and contract mismatches; it cannot confirm runtime ordering, environment state, frequency, or generated behavior without corresponding evidence.

## Depth Rule
- For an obvious local failure with a direct repro, give the decisive cause and fix direction without forcing multiple hypotheses or fix matrices.
- For ambiguous, intermittent, concurrent, security-sensitive, or high-impact failures, show the competing predictions and evidence that eliminated them.
- Compare multiple fixes only when materially different repairs remain after the root cause is known. Do not invent alternatives to fill a template.

## Fix Boundary
- `diagnosis-only`: stop after the causal finding, fix direction, and verification target.
- `diagnosis+fix`: allowed only when the user explicitly asked for both analysis and implementation; use the smallest change that addresses the selected cause.
- A direct “fix this failure” request belongs to `workflow-bug-fix`, which may attach this skill when causal uncertainty is broad.
- If the same failure signature persists after attempted fixes, use `workflow-recovery`.

Never weaken assertions, skip tests, add bypass branches, or broaden mocks merely to remove the signal.

## Output Shape
Lead with the primary root cause and its evidence. Add only what the case needs:

- repro status
- decisive observations and refuted hypotheses
- primary root cause
- fix direction or implemented change
- original-signal verification
- remaining `Unverified` runtime or user checks

Do not turn a narrow RCA into a formal report unless requested.

## Validation
- A confirmed root cause needs a repro, log, test, trace, measurement, or direct observation that distinguishes it from credible alternatives.
- Verification must exercise the original failure condition, not only a nearby passing test.
- Separate checks actually run from user/environment verification still needed.
- If the repro is unavailable, label the conclusion as a leading hypothesis rather than confirmed fact.

## Behavior Cases
- Positive: “간헐적으로 중복 결제가 발생하는 원인을 trace와 상태 흐름으로 RCA해줘.”
- Negative: “이 failing unit test 고쳐줘.” → `workflow-bug-fix`.
- Edge: a missing null guard directly reproduces the failure → report the direct cause; do not fabricate three hypotheses.
- Edge: static call graphs differ from observed runtime ordering → runtime evidence outranks the static lead.

## Known Limits
- No repro or observation means the cause may remain `Unverified`.
- Environment, concurrency, generated code, and external services can invalidate a source-only conclusion.
- Broad redesign belongs to the relevant design or implementation owner after diagnosis.
