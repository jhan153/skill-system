---
name: loop-readiness-router
description: Classify ambiguous loop/goal requests by verifier-feedback value and governance risk before execution.
---

# Loop Readiness Router

## Routing Card
- role: router
- intent_signature:
  - loop readiness, one-shot vs loop, checkpointed work, 반복 실행 판단
- use_when:
  - loop, `/goal`, automation, or repeated-run suitability is requested or unclear.
- do_not_use_when:
  - write a loop contract (`plan-loop-term`), execute an accepted contract (`workflow-loop-runner`), perform obvious direct work, or create a broad planning package.
- expected_inputs:
  - request, domain, verifier hints, side effects, runtime expectations
- expected_outputs:
  - one readiness class, both axes and evidence, missing prerequisites, and next owner
- context_targets:
  must_read:
    - current request or prompt draft
  read_if_needed:
    - `references/readiness-rubric.md` when axes conflict or a checkpoint/capability boundary is ambiguous
    - active plan/spec only when the prompt references it
    - `.codex/docs/orchestration_capability_contract.md` when cron, webhook, queue, automation, durable scheduling, or event-triggered runtime is requested
  do_not_load_by_default:
    - full repo, memory bank, transcripts, or old plans
- risk_profile:
  reads: prompt and narrow target context
  writes: none
  tools: none by default
  sensitive_resources: credentials and live systems are unnecessary
- entry_scene:
  - ROUTE

## Classification
| class | choose when | next path |
| --- | --- | --- |
| `one_shot` | direct outcome, no resume state, and validation does not steer another action | task owner/direct execution |
| `checkpointed_task` | dependent or resumable steps need durable finding state, but not repeated convergence on the same conditions | task owner + `workflow-task-ledger` |
| `contract_needed` | missing material conditions, verifier authority/path, stop/retry/approval terms, or runtime capability prevents a safe readiness or execution decision | `plan-loop-term`; do not execute |
| `loop_worthy` | stable material conditions are authorable and repeated verifier results can change the next implementation action | `plan-loop-term`, then `loop-verifier-registry`; runner only after acceptance |

`loop_worthy` describes the suitable control shape, not permission or activation. `contract_needed` means missing information or governance still prevents that shape from being safely defined.

## Decision Axes
- `feedback_loop_value`: `none` when a final check only confirms a known action; `low` when findings adjust later dependent steps; `high` only when condition-matched verifier evidence repeatedly steers convergence.
- `governance_risk`: `local`, `governed`, or `high` from approvals, side effects, idempotency, rollback, budgets, ownership, and runtime support.

Score them independently. A risky deploy/migration can remain one-shot or checkpointed when its gates are explicit. Missing gates may require a contract; risk alone never creates feedback value.

## Workflow
1. Name the user-visible outcome, material conditions, and evidence/oracle capable of deciding them. Maker self-report or agent-authored tests alone do not establish semantic verifier feedback.
2. Score both axes; record checkpoint need, side-effect gates, and current runtime capability.
3. Apply anti-loop signals: direct answer/command/edit, one final check, repeated identical evidence, or private evidence unavailable to the verifier.
4. Read the rubric only for an actual boundary conflict. Choose the smallest class and one next owner; never execute or draft the contract here.

Words such as `goal`, `loop`, `끝까지`, task length, agent count, or expense do not justify a loop. Durable/event/Wiki/Stop-hook behavior requires current capability evidence; otherwise return the missing prerequisite as unsupported or unverified.

## Output Contract
Return `classification`, minimum-sufficient rationale, both axes with deciding evidence, checkpoint/runtime needs, nonempty prerequisites, verifier hints, next owner, and `verification_status`. Do not emit empty fields or a contract-shaped handoff. For a design loop, name `design-frontend`, `design-visual-regression`, and `design-a11y-audit` as likely downstream owners.

## Validation
- Cite concrete loop/anti-loop signals and keep execution/contract drafting out of this router.
- Do not escalate a simple task, long task, or risky side effect without repeated condition-steering evidence.
- Do not send ambiguous conditions, missing capability, or missing governance directly to execution.
