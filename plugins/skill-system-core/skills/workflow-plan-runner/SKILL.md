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
    - `.codex/docs/delivery_slice_contract.md` when the approved scope needs multiple executable batches, including a wide migration or non-feature decomposition
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
Proceed only when the slice names a material condition, bounded surface or safe discovery, blockers/non-goals, validation target, and no unresolved write approval. Preserve the active user work contract above plan defaults: an approved plan cannot reactivate an explicit exclusion, transfer user-owned verification to the agent, or add interaction the user forbade. Assume only details that cannot change public behavior, source/data ownership, safety, or scope; otherwise block on the exact decision.

## Batch Workflow
1. Resolve the requested scope to its canonical anchor and predecessors. Bind each condition to user/public/canonical/external/formal/observed authority; agent-authored tests may record, not invent, that contract. Classify each proposed batch/action as core, required prerequisite, optional validation/quality, or meta work against the preserved work contract.
2. Choose one coherent batch. If several batches are required, record `delivery_shape` as `vertical_slice`, `migration_sequence`, or `evidence_unit` according to `delivery_slice_contract.md`; do not apply the contract to `single_batch` work. Freeze the surface/non-goals, intended change, blockers, one planned primary verifier, rollback, and approval boundary. A missing verifier lowers evidence authority; it does not create a validation batch.
3. Change the production owner/path and callers, or produce the exact structural artifact when that is the whole condition. Interface/mock/test/scaffold/comment/status-only work is not implementation progress.
4. Validate at matching scope only when the accepted contract assigns validation to the agent and permits that action, using the planned existing verifier, direct observation, or focused smoke check. When verification belongs to the user, hand off as `user-verification-needed` without adding a test framework, mock layer, fixture family, dependency, wrapper, or LoopRun to promote the result label. Behavior, source selection, migration, transforms, external boundaries, and policy-owning adapters still require representative actual-path output/side-effect readback when that path is the material condition and agent validation is in scope.
5. Record only the latest decisive result and preserve conflicting `fail`, `needs_review`, `unverified`, `blocked`, or `user-verification-needed`; lower-scope pass cannot close it. Keep raw logs, receipts, retries, and superseded results out of the plan.
6. Continue through approved scope while required runnable batches remain. A blocked approval or optional validation action is deferred locally and cannot be retried through another form; global `blocked` applies only after independent required batches are exhausted. Route repeated same-signature failure to `workflow-recovery` before another correction.

## Completion Semantics
- `batch_complete`: every material condition has direct evidence; test/interface/mock/document activity cannot replace production work. An exact structural condition may close from matching structural evidence.
- `phase_complete`: every required batch and phase exit gate passed. `plan_complete`: every required phase and final gate passed.
- Never infer `phase_complete` or `plan_complete` from a passing batch, and do not stop after the first passing batch when broader approved scope remains. Select the next batch instead of marking the request complete. Status prose and reporting never change these states.
- When a named user-only product observation remains, stop with `user-verification-needed`; when evidence is unavailable without a user-only check, use `unverified`. Do not extend the plan to manufacture `agent-verified` evidence.
- When material semantic completion otherwise rests mainly on maker-authored implementation and checks, request the `workflow-rigor` standard independent review pass when available; strict risk keeps its two axes separate. Review judgment never replaces the planned condition evidence.
- Missing independent review lowers the task result where material but does not by itself change `batch_complete`, `phase_complete`, or `plan_complete`; it blocks one of those states only when the accepted plan names that review as an exit gate. Any underlying condition that lacks direct evidence remains open regardless.

## Output Contract
Return anchors/batches, changed implementation and callers, condition authority/evidence/status, rollback or blocker, next batch, and directly known phase/plan status. Separate batch, requested-scope, phase, and plan completion.

## Cross-Skill Boundaries
- `plan-short-term-docs` owns short plans; `workflow-implementation` owns and may write direct features; `workflow-validation` owns validation-only design; `coordination-handoff` owns handoffs; `workflow-recovery` owns repeated failure. Planning/reporting cannot implement or complete a batch.
