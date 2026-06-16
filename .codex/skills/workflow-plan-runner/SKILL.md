---
name: workflow-plan-runner
description: Executes an approved plan, spec, or plan package into implementation batches. Use when the user asks to implement from an existing plan/spec/package, run a phase, build an initial waterfall-style version from requirements, or execute a planned scope rather than create the plan.
---

# Workflow Plan Runner

## Routing Card
- role: primary
- intent_signature:
  - approved plan execution
  - spec-driven implementation
  - plan package execution
  - Phase 1 실행
  - 기획서 기반 초기 구현
  - waterfall-style initial build
- use_when:
  - the user asks to execute an approved short-term plan, long-term package, or spec.
  - the user asks for initial implementation from a requirements/spec document rather than more planning.
  - a large planned scope should be implemented in change batches with validation after each batch.
- do_not_use_when:
  - the user asks to create or update the plan/spec/package; use `plan-short-term-docs` or `plan-long-term-package`.
  - the task is a small direct edit that does not need plan/spec execution orchestration.
  - the plan/spec is missing and the user has not provided enough requirements to execute safely.
  - the request is handoff-only or multi-agent ownership only; use `coordination-brief` or `coordination-multi-agent`.
- expected_inputs:
  - approved plan, spec, requirements document, or package pointer
  - target phase, batch, or implementation slice
  - repo write scope and validation expectations
- expected_outputs:
  - execution slice, batch order, changed implementation artifacts, validation per batch, rollback/fallback decision when needed, status updates, and remaining gaps
- context_targets:
  must_read:
    - current execution request
    - approved plan/spec/package slice that owns the scope
    - target source/test/config files for the current batch
  read_if_needed:
    - active short-term plan for status sync
    - long-term package README or relevant phase docs
    - validation contract
    - coordination notes when multiple owners are explicit
  do_not_load_by_default:
    - full repo
    - full memory bank
    - all plan packages
    - unrelated specs
    - archived raw plans
- risk_profile:
  reads:
    - approved plan/spec slice, targeted source files, tests, and validation output
  writes:
    - WRITE_CODEBASE for the approved implementation slice; plan/status docs only when explicitly in scope
  tools:
    - CALL_PROCESS for targeted build/test/smoke checks tied to the current batch
  sensitive_resources:
    - credentials default deny; destructive, network, data, or external-side-effect steps require explicit boundary review
- entry_scene:
  - PREPARE

## Purpose
- Convert an approved plan/spec into real implementation batches.
- Own "what to implement next" for plan-driven work.
- Keep planning, coordination, validation, and reporting as separate support layers.

## Activation
- Primary for "이 스펙대로 구현", "이 plan package Phase 1 실행", "기획서 기반으로 초기 구현", or "waterfall식으로 전체 골격 구현" requests.
- Attach `workflow-rigor` for medium/high-risk execution discipline.
- Attach `workflow-validation` for validation matrix or validation-only substeps.
- Attach `coordination-brief` or `coordination-multi-agent` only for explicit handoff, lock scope, or multi-agent ownership.

## Workflow
1. Confirm the plan/spec/package is approved or sufficient for execution.
2. Select the smallest executable slice for the current turn.
3. Lock scope: files/modules, non-goals, risk boundary, and validation target.
4. Build a batch order: each batch has change intent, expected artifact, and validation.
5. Implement one batch at a time.
6. Validate each batch before expanding scope.
7. Sync status to the active plan only when plan status tracking is explicitly in scope.
8. Report changed implementation artifacts, validation, remaining gaps, and next batch.

## Execution Source Checklist
Treat the plan/spec/package as sufficient for execution only when it provides:
- target behavior or acceptance criteria for the current slice
- implementation boundary: files, modules, routes, services, or artifacts likely to change
- non-goals or deferred scope when the plan is broad
- validation expectation or enough context to derive one
- no unresolved approval marker that blocks writes

If one item is missing but the safe implementation slice is still obvious, proceed and mark the assumption. If two or more are missing, stop and report the missing execution source instead of inventing the plan.

## Output Contract
Return only the sections needed:
- `execution_scope`
- `batch_plan`
- `changed_artifacts`
- `validation_per_batch`
- `rollback_or_fallback`
- `blocked_items`
- `remaining_gaps`
- `next_batch`

## Rollback And Fallback
- Continue normal execution when validation passes or failures are unrelated to the current batch.
- Re-run validation only when the command, environment, or fixture is suspect and the changed code is not implicated.
- Hand off to `workflow-recovery` when the same failure signature repeats after a targeted fix or when fake-fix pressure appears.
- Roll back or isolate the last batch when it introduced a regression and the cause is not understood.
- Stop execution and report `blocked` when the plan/spec is insufficient, validation cannot be run, or the next batch would exceed the approved scope.

## Completion Gate
- Completion requires source, test, runtime config/build, or executable scaffold changes tied to the approved plan/spec.
- Plan-only, spec-only, report-only, or TODO-only edits do not satisfy implementation completion.
- If no executable slice is safe, report `blocked` with the exact missing input or approval boundary.

## Invocation Examples
Positive:
- "이 승인된 스펙대로 Phase 1 초기 구현을 진행해줘."
- "이 plan package의 Batch 2를 실제 코드로 실행해줘."
- "기획서 기반으로 MVP 골격을 먼저 구현해줘."

Negative:
- "이 스펙 초안을 보고 구현 계획만 더 다듬어줘." -> `plan-short-term-docs`
- "이 변경을 어떻게 검증할지만 matrix로 짜줘." -> `workflow-validation`
- "같은 테스트가 계속 실패해. 원인 하나씩 격리하자." -> `workflow-recovery`

## Cross-Skill Boundaries
- `plan-short-term-docs` owns short-term plan document creation and synchronization.
- `plan-long-term-package` owns multi-document package creation.
- `workflow-rigor` owns evidence depth and completion discipline.
- `workflow-validation` owns validation strategy and validation-only runs.
- `coordination-*` owns handoff and ownership notes, not execution order.
- `report-*` owns final presentation, diff, artifact inventory, or critical verdicts.

## Known Limits
- This skill assumes an executable source of truth exists.
- It does not invent missing specs or turn ambiguous requirements into implementation without marking uncertainty.
- It does not create persistent workflow state or multi-agent event logs.
