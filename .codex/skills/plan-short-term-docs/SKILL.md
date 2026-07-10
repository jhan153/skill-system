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

## State And Horizon Boundary
- Treat short term as the current executable design horizon, not a calendar duration.
- Admit `create_active_plan` only when the user requests a persisted plan or an active plan already owns the task.
- Own synchronization of `active_plan` and the `approve_implementation` gate to `implementation_ready`.
- Do not execute production work. After approval, hand implementation to `workflow-plan-runner` or the task-specific workflow and remain only a secondary status tracker.
- Use `plan-long-term-package` when one plan cannot safely hold the cross-session phases/contracts; use `workflow-task-ledger` when only lightweight next-turn state is needed.

## Staged Context Admission
1. Read the request and explicit plan pointer. If absent, inspect only `docs/plan` names/metadata for a matching active plan; do not open every plan.
2. For a new plan, read `references/plan-template.md`. For an existing plan, load only that plan and preserve its stable task/state identifiers.
3. Read the source outline, target files, or validation contract only to resolve affected boundaries, file paths, risks, or checks.
4. Admit memory or historical plans only when a current decision depends on them; prefer a summary over raw text.

If the goal stays ambiguous, record one focused question or a marked assumption. Never recover by loading the full repo, memory bank, or plan history.

## Plan Authoring Workflow
1. State objective, bounded scope, non-goals, current state, and observable success conditions.
2. List concrete target files/components. When unknown, create a bounded discovery TODO instead of guessing paths.
3. Describe what changes and why, then connect each change to risks, validation evidence, and an ordered TODO.
4. Record decisions and open questions with source/evidence and blocking status.
5. Define validation commands or manual scenarios with expected signals; mark unavailable checks `Unverified`.
6. Record the planning-state transition block and progress log.
7. Run the Plan Quality Gate before reporting the plan path and next action.

## Required Plan Contract
Create or update `docs/plan/YYYY-MM-DD-<task-slug>.md` with at least:

- objective, scope, and non-goals
- changed-file/component list
- change summary (`what` / `why`)
- current versus target state where materially useful
- risks and mitigations
- validation procedure and expected evidence
- `질의` with answer/decision status
- ordered TODOs with `todo`, `doing`, `done`, or `blocked`
- implementation-transition record
- progress log

Reuse the existing active file for the same task. Keep sections consistent; do not let TODO, status, approval, and progress claims contradict each other.

## Plan Quality Gate
- **Scope:** the plan fits one current execution horizon; deferred work is explicit.
- **Traceability:** every material change maps to a file/component or discovery task, a TODO, a risk, and acceptance evidence.
- **Actionability:** each TODO has an outcome, dependencies/blocker, and completion signal; the first executable item is obvious.
- **Validation:** checks address the success conditions and name expected pass signals, not only commands.
- **Decisions:** unresolved product/interface decisions are visible and block dependent TODOs when necessary.
- **Evidence:** planned facts come from admitted source; guesses are assumptions or `Unverified`.
- **State:** the transition block records `current_state`, attempted event, approval phrase/evidence, accepted or rejected result, and next state.

Do not pad the plan with placeholder code or diagrams. Include real before/after code in separate language-matched blocks only when it materially clarifies a planned change. Add a diagram only for runtime interaction, component/class boundary, concurrency, or data-model structure—not agent workflow or approval flow.

## Implementation Transition Gate
Accept `approve_implementation` only when:

1. the plan is currently `active_plan`;
2. its scope is explicit and current;
3. wording such as `이 플랜대로 구현 시작`, `플랜 구현해`, or an equivalent instruction clearly applies to this task; and
4. runtime/sandbox policy permits the requested mutation.

Reject a one-word `승인`, `작업해`, or `구현해` when surrounding context does not identify the active scope. Reject completed, closed-out, archived, superseded, or merely historical plans unless the user explicitly re-admits one for the current task.

Before acceptance, edit plan artifacts only. On acceptance:

- record timestamp, approval evidence, and `current_state: implementation_ready` before or with the first implementation update;
- freeze the accepted plan baseline;
- hand execution to the implementation owner in TODO order;
- keep plan TODO/status updates as secondary bookkeeping;
- never report implementation complete from a plan-only diff unless the request was documentation-only.

Implementation completion requires source, test, runtime config/build, or executable scaffold evidence, or an exact blocker/analysis-only result.

## Research Boundary
Let `research-hypothesis-planning` own hypothesis, experiment, ablation, loss, or training-plan content. Use this skill only to persist that accepted content under `docs/plan`. Do not route ordinary development planning to research merely because it mentions a model, metric, experiment, or loss.

## Conversation Synchronization
On each planning turn, update decisions, `질의`, TODOs, risks, validation, and transition state in the plan—not only in chat. During implementation, append newly discovered ambiguity or scope as a question/TODO and keep status synchronized without taking execution ownership.

## Reporting And Limits
Report the active plan path, current state, accepted/rejected event with evidence, changed plan sections, and exactly one next action. A plan is design evidence, not proof of feasibility or runtime correctness; mark stale or unavailable evidence accordingly.
