---
name: plan-short-term-docs
description: Create or synchronize a persisted docs/plan artifact for the current executable design horizon, including scope, files, risks, validation, decisions, TODOs, and implementation-transition state. Use only when the user requests a plan artifact or an active plan already owns the task.
disable-model-invocation: true
---

# Plan Short Term Docs

## Routing Card
- role: primary
- intent_signature:
  - create or update a persisted `docs/plan` artifact
  - synchronize an active plan, decisions, TODOs, or transition state
- use_when:
  - the user requests a current-horizon plan document under `docs/plan`.
  - an explicitly referenced active plan already owns the planning conversation.
- do_not_use_when:
  - `plan` is only a casual word.
  - the user asks for direct implementation without plan synchronization; execution remains task-workflow-owned.
  - the task is a small local edit, conceptual answer, task ledger, or multi-phase package.
- expected_inputs:
  - planning objective, active plan path when available, decisions, risks, tasks, and validation strategy
- expected_outputs:
  - one synchronized active plan and an evidence-backed implementation-transition verdict
- context_targets:
  must_read:
    - current planning request
    - active plan or `references/plan-template.md` for a new plan
  read_if_needed:
    - affected source outline and target slices
    - relevant memory cards and validation contract
    - `.claude/docs/planning_state_model.md` when state admission is ambiguous
    - `.claude/docs/delivery_slice_contract.md` when execution needs multiple batches, including wide migration or non-feature decomposition
  do_not_load_by_default:
    - full repo, memory bank, all plans, or phase-package templates
- risk_profile:
  reads:
    - active plan and narrow implementation evidence
  writes:
    - `docs/plan` only before an accepted implementation transition
  tools:
    - targeted file discovery or validation lookup only when needed
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Contract And Context
- Short term means one current executable design horizon, not a calendar duration. Activate only for an explicitly requested persisted plan or an already owning active plan.
- Own `active_plan` synchronization and the gate to `implementation_ready`; never own production execution. After acceptance, hand work to `workflow-plan-runner` or the task workflow and remain a secondary tracker.
- Use `plan-long-term-package` for cross-session phases/contracts and `workflow-task-ledger` for lightweight next-turn state.

Read the explicit plan pointer first. Without one, inspect only `docs/plan` names or metadata for a matching active plan. For a new plan read `references/plan-template.md`; for an existing plan read only that file and preserve stable identifiers. Admit source outlines, validation contracts, memory, or history only when needed to resolve a material path, risk, check, or decision. Record one focused question or marked assumption instead of loading broad context.

## Author And Synchronize
1. Create `docs/plan/YYYY-MM-DD-<task-slug>.md` from the template, or reuse the task's active file. The template is the format owner.
2. Record objective, bounded scope/non-goals, observable success, concrete files/components, what/why, risks, decisions/questions, ordered implementation TODOs, one primary verifier, transition state, and a compact current snapshot. If execution needs several batches, record `delivery_shape` as `vertical_slice`, `migration_sequence`, or `evidence_unit`; omit the delivery contract for `single_batch` work. Use a bounded discovery TODO instead of guessing paths.
3. Map each material change to its owner/path and completion signal. Prefer an existing repository verifier, direct-path observation, or a small smoke check. If none is available, record `user-verification-needed`; do not create a test framework, mock layer, fixture family, or validation phase solely to improve the result label.
4. Keep validation bounded to the latest decisive result for each material condition. Raw command output, receipts, retry history, repeated passes, and superseded failures stay out of the plan. A rerun replaces the prior result instead of appending another progress entry.
5. Treat tests, mocks, and validation helpers as implementation scope only when the user requested them or they directly cover a material regression risk with an already anchored expectation. Agent-authored checks remain supporting evidence; missing independent evidence lowers the result label rather than expanding the plan.
6. Keep decisions, `질의`, TODO status, risks, validation, transition, and the current snapshot consistent by replacing stale state, not by accumulating a chronological execution log.

Do not pad plans with placeholder code or diagrams. Follow the template's conditional code/diagram rules.

## Plan Quality Gate
- Scope fits one execution horizon and deferred work is explicit.
- The first executable TODO is clear; each TODO has an outcome, dependency/blocker, and completion signal.
- Multi-batch TODOs follow `.claude/docs/delivery_slice_contract.md` and name exactly one applicable `delivery_shape`; single-batch work does not import slice ceremony.
- Material changes trace to evidence and unresolved product/interface decisions block dependent work.
- Validation names one smallest primary verifier and an optional user-only check; unavailable evidence does not create new implementation scope.
- No test, mock, fixture, dependency, or loop work exists solely to manufacture completion evidence.
- State records the attempted event, approval evidence, accepted/rejected result, and next state without contradicting TODO/progress claims.

Passing this gate proves plan readiness only, not feasibility, implementation, runtime correctness, or user success.

## Implementation Transition
Accept `approve_implementation` only when the plan is `active_plan`, scope is explicit/current, the user's wording unambiguously applies to this task (for example `이 플랜대로 구현 시작`), and runtime policy permits mutation. Reject context-free `승인`, `작업해`, or `구현해`, and reject closed, archived, superseded, or historical plans unless explicitly re-admitted.

Before acceptance, edit plan artifacts only. On acceptance, record timestamp and approval evidence, set `current_state: implementation_ready`, freeze the accepted baseline, and hand TODO-ordered execution to its owner. `implementation_ready` is not implementation completion. Never mark a material condition done from a plan-only diff, lower-scope pass, or unresolved `needsReview`; require same-condition source/runtime/readback evidence or record it as unresolved.

## Reporting And Boundaries
Report the active plan path, current state, changed sections, and exactly one next action. Do not quote raw verifier logs or enumerate superseded attempts. Let `research-hypothesis-planning` own research design content; this skill only persists accepted content. A plan remains design evidence, and stale or unavailable implementation evidence stays explicit without spawning validation-only work.
