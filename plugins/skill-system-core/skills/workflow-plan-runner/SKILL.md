---
name: workflow-plan-runner
description: Execute an approved plan/spec as source-anchored batches; real implementation and matching evidence gate batch, phase, and plan completion.
---

# Workflow Plan Runner

## Routing Card
- role: primary
- intent_signature:
  - approved plan/spec phase or batch implementation; 기획서 기반 구현
- use_when:
  - the user asks to execute an approved plan/spec/package phase or batch beyond an ordinary direct edit.
- do_not_use_when:
  - creating/revising/reviewing a plan, direct implementation without plan dependency, validation-only design, handoff-only recording, or repeated failure recovery is primary.
- expected_inputs:
  - canonical source/slice, material conditions and non-goals, target surface, dependencies, and validation/side-effect boundary
- expected_outputs:
  - approved scope implemented in smallest batches with condition evidence and separate batch/phase/plan status
- context_targets:
  must_read:
    - request, owning source slice, and next batch's implementation surface
  read_if_needed:
    - blocker, canonical oracle, actual-path evidence, or requested status/coordination contract
  do_not_load_by_default:
    - full repo/plan history, unrelated specs/logs, production data, or credentials
- risk_profile:
  reads: approved slice and targeted implementation/evidence path
  writes: approved slice; plan state only when requested and evidenced
  tools: condition-matched build/runtime/readback
  sensitive_resources: external side effects keep their governing approval boundary
- entry_scene:
  - SOURCE_GATE

## Source Gate
Proceed only when the slice names a material condition, bounded surface or safe discovery, blockers/non-goals, validation target, and no unresolved write approval. Assume only details that cannot change public behavior, source/data ownership, safety, or scope; otherwise block on the exact decision.

## Batch Workflow
1. Resolve the requested scope to its canonical anchor and predecessors. Bind each condition to user/public/canonical/external/formal/observed authority; agent-authored tests may record, not invent, that contract.
2. Choose one coherent batch. Freeze its surface/non-goals, intended change, evidence, rollback, and approval boundary.
3. Change the production owner/path and callers, or produce the exact structural artifact when that is the whole condition. Interface/mock/test/scaffold/comment/status-only work is not implementation progress.
4. Validate at matching scope. Behavior, source selection, migration, transforms, external boundaries, and policy-owning adapters require representative actual-path output/side-effect readback. Structural checks, commands, tests, and mocks retain their narrower scope.
5. Record the delta and preserve conflicting `fail`, `needs_review`, `unverified`, `blocked`, or `user-verification-needed`; lower-scope pass cannot close it. Keep one authoritative source and fail closed on required canonical absence/mismatch.
6. Continue through approved scope while batches pass. Stop at a blocker, approval/user gate, requested batch, or completed scope; route repeated same-signature failure to `workflow-recovery` before another correction.

## Completion Semantics
- `batch_complete`: every material condition has direct evidence; test/interface/mock/document activity cannot replace production work. An exact structural condition may close from matching structural evidence.
- `phase_complete`: every required batch and phase exit gate passed. `plan_complete`: every required phase and final gate passed.
- Never infer `phase_complete` or `plan_complete` from a passing batch, and do not stop after the first passing batch when broader approved scope remains. Select the next batch instead of marking the request complete. Status prose and reporting never change these states.

## Output Contract
Return anchors/batches, changed implementation and callers, condition authority/evidence/status, rollback or blocker, next batch, and directly known phase/plan status. Separate batch, requested-scope, phase, and plan completion.

## Cross-Skill Boundaries
- `plan-short-term-docs` owns short plans; `workflow-implementation` owns and may write direct features; `workflow-validation` owns validation-only design; `coordination-handoff` owns handoffs; `workflow-recovery` owns repeated failure. Planning/reporting cannot implement or complete a batch.
