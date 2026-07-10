---
name: workflow-plan-runner
description: Executes an approved plan or spec as the smallest safe implementation batch, preserving plan scope and distinguishing batch completion from whole-plan completion.
---

# Workflow Plan Runner

## Routing Card
- role: primary
- intent_signature:
  - approved plan or spec execution
  - target phase or batch implementation
  - 기획서 기반 구현
- use_when:
  - the user asks to implement an approved plan/spec/package or a named phase/batch.
  - a broad approved scope needs ordered implementation batches.
- do_not_use_when:
  - the user asks to create, revise, review, or merely summarize the plan.
  - a direct edit has no plan-execution dependency.
  - no executable source is provided and material requirements cannot be derived safely.
- expected_inputs:
  - approved execution source and requested slice
  - target code/config/tests and validation boundary
- expected_outputs:
  - the approved request scope implemented as the smallest validated batches
  - explicit per-batch status and evidence-backed phase/whole-plan status
- context_targets:
  must_read:
    - current execution request
    - only the plan/spec/package slice that owns the requested scope
    - target source, tests, and config for the next batch
  read_if_needed:
    - relevant dependency phase or canonical contract
    - active plan status fields when synchronization is requested
    - validation or coordination contract when explicitly attached
  do_not_load_by_default:
    - full repo
    - all plan packages or phase docs
    - archived plans and unrelated specs
- risk_profile:
  reads:
    - approved slice and targeted implementation evidence
  writes:
    - approved codebase slice; plan status only when requested
  tools:
    - targeted build, test, or smoke checks
  sensitive_resources:
    - external side effects require their normal approval boundary
- entry_scene:
  - SOURCE_GATE

## Execution Source Gate

Proceed only when the current slice identifies:

- observable behavior or acceptance criteria
- bounded implementation surface or a safe discovery step
- blocking dependencies and non-goals
- a validation target
- no unresolved approval marker for the proposed write

A missing detail may be recorded as an assumption only when it cannot alter public behavior, data ownership, safety, or scope. Otherwise stop with the exact missing decision; do not invent requirements from neighboring plan prose.

## Batch Contract

Choose the smallest batch that closes one observable condition. A batch is the validation unit, not the default stopping point: continue through the user's approved request scope while each batch passes and no blocker, approval boundary, or user stop is reached. Record:

| Field | Meaning |
| --- | --- |
| `source_anchor` | exact plan/spec condition owned by this batch |
| `scope` | files/components and explicit non-goals |
| `change` | one coherent implementation outcome |
| `validation` | check that can confirm or reject that outcome |
| `status` | `passed`, `failed`, `blocked`, or `user-verification-needed` |

Do not open the next batch until the current batch is passed or explicitly isolated. Attach `workflow-recovery` after a same-signature failure repeats; attach `workflow-validation` only when check design is itself the task.

## Workflow

1. Resolve the requested phase/batch to its canonical source anchor and blocking predecessors.
2. Apply the execution-source gate and freeze the current batch scope.
3. Inspect only the implementation surface needed for that batch.
4. Implement and run its targeted validation.
5. Record condition delta and evidence; synchronize plan state only when requested.
6. If approved request scope remains, select the next batch and repeat. Stop only when that scope is complete, a blocker/approval/user-verification gate is reached, or the user requested a single batch.

## Completion Semantics

- `batch_complete`: every condition in the current batch passed with evidence.
- `phase_complete`: all required batches and phase exit gates passed.
- `plan_complete`: every required phase and final plan gate passed.

Never infer `phase_complete` or `plan_complete` from one successful batch. Conversely, do not stop after the first passing batch when the user approved a broader executable scope. Documentation-only status updates do not complete an implementation batch. If no safe executable slice exists, the result is `blocked`, not completion.

## Output Contract

Report only:

1. `source_anchor` and executed batch scopes
2. changed implementation artifacts by batch
3. validation evidence and status per batch
4. `phase_status` / `plan_status` only when known from the execution source
5. next approved batch or the single blocker

## Boundaries And Validation

- Planning skills own plan creation; this skill consumes approved execution sources.
- Coordination skills own handoff/ownership records, not implementation order.
- Reporting skills may format the result but do not change completion state.
- Confirm the diff stays within the batch source anchor and that material acceptance conditions have direct evidence.
