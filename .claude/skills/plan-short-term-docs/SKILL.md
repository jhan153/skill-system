---
name: plan-short-term-docs
description: Create or synchronize a persisted docs/plan artifact for the current executable design horizon, including scope, files, risks, validation, decisions, TODOs, and implementation-transition state. Use only when the user requests a plan artifact or an active plan already owns the task.
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
    - `.codex/docs/planning_state_model.md` when state admission is ambiguous
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
2. Record objective, bounded scope/non-goals, observable success, concrete files/components, what/why, risks, decisions/questions, ordered TODOs, validation, transition state, and progress. Use a bounded discovery TODO instead of guessing paths.
3. Map every material change to an owner/path or discovery task, TODO, risk, and acceptance evidence. Define expected signals, not commands alone; include actual production or user-path readback when that is the material condition.
4. Mark unavailable evidence `Unverified`. Structural checks, mocks, and agent-authored tests prove only their stated contracts and cannot override conflicting actual-path evidence. When a material condition fails, keep its TODO unresolved and record the exact resolution plus renewed same-path readback required to close it.
5. Keep decisions, `질의`, TODO status, risks, validation, transition, and progress consistent in the artifact on every planning turn.

Do not pad plans with placeholder code or diagrams. Follow the template's conditional code/diagram rules.

## Plan Quality Gate
- Scope fits one execution horizon and deferred work is explicit.
- The first executable TODO is clear; each TODO has an outcome, dependency/blocker, and completion signal.
- Material changes trace to evidence and unresolved product/interface decisions block dependent work.
- Validation covers success conditions with expected signals and calibrated evidence scope.
- State records the attempted event, approval evidence, accepted/rejected result, and next state without contradicting TODO/progress claims.

Passing this gate proves plan readiness only, not feasibility, implementation, runtime correctness, or user success.

## Implementation Transition
Accept `approve_implementation` only when the plan is `active_plan`, scope is explicit/current, the user's wording unambiguously applies to this task (for example `이 플랜대로 구현 시작`), and runtime policy permits mutation. Reject context-free `승인`, `작업해`, or `구현해`, and reject closed, archived, superseded, or historical plans unless explicitly re-admitted.

Before acceptance, edit plan artifacts only. On acceptance, record timestamp and approval evidence, set `current_state: implementation_ready`, freeze the accepted baseline, and hand TODO-ordered execution to its owner. `implementation_ready` is not implementation completion. Never mark a material condition done from a plan-only diff, lower-scope pass, or unresolved `needsReview`; require same-condition source/runtime/readback evidence or record it as unresolved.

## Reporting And Boundaries
Report the active plan path, current state, accepted/rejected event with evidence, changed sections, and exactly one next action. Let `research-hypothesis-planning` own research design content; this skill only persists accepted content. A plan remains design evidence, and stale or unavailable implementation evidence stays explicit.
