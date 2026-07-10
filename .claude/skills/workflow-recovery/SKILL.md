---
name: workflow-recovery
description: Recovers repeated failure loops during implementation or validation. Use when the same test/build/runtime failure repeats, prior fixes did not resolve the issue, fake-fix risk is high, or the user asks to isolate one cause and break the retry loop.
---

# Workflow Recovery

## Routing Card
- role: primary
- intent_signature:
  - repeated failure loop, same test still failing, fake-fix prevention, recovery mode, 범위 줄여서 원인 격리, 실패 루프 복구
- use_when:
  - the same stable failure signature reappears after at least one attempted fix, rerun adjustment, or recovery action.
  - the user explicitly asks to stop fake fixes, isolate one cause, or recover a stuck implementation.
- do_not_use_when:
  - this is the first observation of an ordinary bug; use `analysis-bug` when root cause is the task.
  - the request is only to rerun a known command once, or the issue is already solved.
  - the user wants broad redesign, planning, or reporting rather than recovery execution.
- expected_inputs:
  - failing command or user-observed symptom and decisive output
  - latest attempted change or fix summary
  - expected success signal and current blocker
- expected_outputs:
  - stable failure fingerprint and recovery status
  - one falsifiable hypothesis, one diagnostic or fix, and decisive revalidation
  - rollback/fallback decision and one next action
- context_targets:
  must_read:
    - current failure evidence
    - latest relevant diff or attempted-fix summary
    - original success check when available
  read_if_needed:
    - implicated source and smallest reproducer
    - active spec only when it defines expected behavior
    - environment or dependency facts only when the hypothesis implicates them
  do_not_load_by_default:
    - full repo, full memory bank, unrelated logs, or broad transcripts
- risk_profile:
  reads:
    - failure evidence, latest diff, targeted source, and decisive checks
  writes:
    - at most one narrowed fix per hypothesis after evidence justifies it
  tools:
    - focused reproduction, one diagnostic, and targeted revalidation
  sensitive_resources:
    - credentials default deny; destructive recovery requires separate authorization
- entry_scene:
  - PREPARE

## Entry Gate
Enter recovery when the failure fingerprint is materially unchanged after an attempted intervention, or immediately on explicit user request.

Fingerprint on command/user path, failing phase/test/symbol, and the first stable causal error, assertion, exit class, or observed mismatch. Normalize away timestamps, temporary paths, random identifiers, ordering noise, and wrapper frames. Similar wording is not the same fingerprint when the causal error changed; classify that result as `moved`.

## Recovery Invariant
Maintain exactly one active hypothesis and one evidence-changing action at a time. Record the predicted observation before acting; do not stack fixes, broaden scope, or change the success signal while the hypothesis is active.

## Protocol
1. Freeze the loop: record `failure_fingerprint`, original success check, latest intervention, and whether that intervention changed the signal.
2. Reduce to the smallest reproducer that preserves the fingerprint. If reproduction is impossible, switch to evidence capture rather than patching.
3. Select one falsifiable hypothesis. State its evidence basis and predicted observation.
4. Choose the cheapest action that can distinguish the hypothesis: a focused diagnostic first, or one targeted fix only when existing evidence already isolates the cause.
5. Re-run the focused reproducer and the original success check when feasible.
6. Classify the result and decide whether to keep or isolate the change.

## Result Classification

| status | meaning | required next step |
| --- | --- | --- |
| `resolved` | original success check passes and no contradictory signal remains | finish with decisive evidence |
| `narrowed` | failure persists but scope or cause is more specific | record the eliminated alternative, then choose one new hypothesis |
| `moved` | stable causal signature changed | keep the change only if the movement is explained; fingerprint the new failure |
| `unchanged` | same fingerprint remains and the action added no information | isolate/revert the action when it adds uncertainty; record the hypothesis as disproven or unsupported |
| `unreproducible` | decisive signal cannot be observed | request/capture the missing evidence; do not patch |

If `unchanged` occurs twice inside recovery, stop modifying. Report the exact missing evidence, access, or decision needed for one next action.

## Anti-Fake-Fix Rules
- Never weaken tests, assertions, criteria, or logs to make the signal disappear.
- Never add a bypass branch without an evidenced cause and explicit risk treatment.
- Never call the issue fixed because a different or narrower check passes.
- Never retain a speculative change that leaves the original signal unchanged and increases uncertainty.

## Capability Ceiling
If further progress requires an unavailable oracle, environment, permission, tool capability, or quality judgment that the current evidence cannot supply, name that ceiling. Do not disguise it as another procedure retry; return `blocked` with the single evidence/access action that would reopen recovery.

## Output Contract
Lead with `status` and return only:

- `failure_fingerprint`
- `decisive_evidence`
- `active_hypothesis`
- `diagnostic_or_fix`
- `validation_result`
- `keep_or_rollback`
- `remaining_blocker`
- `next_recovery_action`

Omit empty fields. `next_recovery_action` must be one action, not an option list.

## Boundaries
- `analysis-bug` owns first-pass or broad root-cause analysis before a retry loop exists.
- `workflow-validation` owns a new validation matrix; `workflow-rigor` may constrain a risky recovery fix.
- `workflow-plan-runner` owns plan order; recovery temporarily owns only the stuck failure slice.
- `report-critical` owns review verdicts, not recovery execution.

## Validation
- The entry gate is supported by a stable fingerprint or explicit recovery intent.
- Exactly one hypothesis and one diagnostic/fix were active.
- Revalidation includes the original success signal or states why it could not run.
- The result is classified as `resolved`, `narrowed`, `moved`, `unchanged`, or `unreproducible` from observed evidence.
- No test, assertion, log, or criterion was weakened to claim progress.
- Repeated `unchanged` outcomes stop with one concrete blocker action.
