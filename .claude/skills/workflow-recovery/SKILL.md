---
name: workflow-recovery
description: Recovers repeated failure loops during implementation or validation. Use when the same test/build/runtime failure repeats, prior fixes did not resolve the issue, fake-fix risk is high, or the user asks to isolate one cause and break the retry loop.
---

# Workflow Recovery

## Routing Card
- role: primary
- intent_signature:
  - repeated failure loop, fake-fix prevention, recovery mode, 범위 줄여서 원인 격리, 실패 루프 복구
- use_when:
  - a stable material failure reappears after an attempted intervention.
  - the user explicitly asks to stop fake fixes, isolate one cause, or recover a stuck implementation.
- do_not_use_when:
  - this is a first ordinary bug (`analysis-bug`), one known rerun, or an already-solved issue.
  - the user wants broad redesign, planning, or reporting rather than recovery execution.
- expected_inputs:
  - failing command or user path, decisive output, latest intervention, and material success signal
- expected_outputs:
  - stable fingerprint, one hypothesis/action, decisive revalidation, keep/rollback decision, and one next action
- context_targets:
  must_read:
    - current failure evidence, latest intervention/diff, and original material signal when available
  read_if_needed:
    - implicated source, smallest reproducer, controlling spec, and hypothesis-relevant environment facts
  do_not_load_by_default:
    - full repo, unrelated logs, memory banks, or broad transcripts
- risk_profile:
  reads: failure evidence, latest diff, targeted source, and decisive checks
  writes: at most one narrowed fix per hypothesis after evidence justifies it
  tools: focused reproduction, one diagnostic, and targeted revalidation
  sensitive_resources: credentials default deny; destructive recovery requires separate authorization
- entry_scene:
  - PREPARE

## Entry And Invariant
Enter when a material failure fingerprint remains after an intervention, or immediately on explicit recovery intent. Fingerprint the command/user path, failing phase/test/symbol, and first stable causal error, assertion, exit class, or observed mismatch. Ignore timestamps, temporary paths, random IDs, ordering noise, and wrapper frames; a changed causal error is `moved`.

Keep exactly one active hypothesis and one evidence-changing action; the hypothesis must be falsifiable. Record its predicted observation first. Do not stack fixes, broaden scope, or replace the original material success signal with an easier proxy.

## Protocol
1. Freeze `failure_fingerprint`, user-relevant success condition, evidence scope/oracle, latest intervention, and observed effect.
2. Find the smallest reproducer that preserves the fingerprint without replacing the original signal. If no decisive signal is observable, capture missing evidence instead of patching.
3. State one hypothesis, basis, and predicted observation. Use the cheapest discriminating diagnostic, or one targeted production fix only when evidence isolates the cause.
4. Re-run the reproducer and original success check, then read back the material path when feasible. Mock, unit, structural, generated-artifact, or narrower passes prove only their boundary and cannot overrule conflicting real-path evidence. After a targeted owner fix, repeat that same material-path readback.
5. Classify the observation. Keep an explained change; otherwise isolate or roll it back.

## Result Classification

| status | meaning | required next step |
| --- | --- | --- |
| `resolved` | the original material success signal passes at its required scope and no contradiction remains | finish with decisive evidence |
| `narrowed` | new evidence eliminates a causal alternative in the failing material path | record the eliminated alternative, then choose one new hypothesis |
| `moved` | stable causal signature changed | keep the change only if the movement is explained; fingerprint the new failure |
| `unchanged` | same fingerprint remains and the action added no information | isolate/revert the action when it adds uncertainty; record the hypothesis as disproven or unsupported |
| `unreproducible` | decisive signal cannot be observed | request/capture the missing evidence; do not patch |

## Stop And Integrity Rules
- A lower-scope pass alone leaves the material status `unchanged`; it is not `narrowed` evidence.
- If `unchanged` occurs twice, stop modifying, use task result `blocked`, and name one missing-evidence, access, or decision action.
- Never weaken a test, assertion, criterion, or log; add an unevidenced bypass; or call a narrower pass a fix.
- Do not retain a speculative change that leaves the original signal unchanged and increases uncertainty.
- If the needed oracle, environment, permission, capability, or judgment is unavailable, use task result `blocked` with the single reopening action. Do not launder the ceiling through another retry.
- Use `agent-verified` only when status is `resolved` and every material condition is met; omit task labels while recovery continues.

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
- `result_label` only at task closeout

Omit empty fields. `next_recovery_action` must be one action, not an option list.

## Boundaries And Validation
- `analysis-bug` owns first-pass/broad diagnosis; validation, rigor, plan-running, and review owners keep their existing scopes.
- Recovery owns only the stuck slice. A valid result has a supported entry, one hypothesis/action, observed classification, and original-signal revalidation or an explicit reason it was unavailable.
- Do not claim progress by weakening evidence. Repeated `unchanged` outcomes stop with one concrete blocker action.
