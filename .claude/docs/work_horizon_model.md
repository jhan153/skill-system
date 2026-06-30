# Work Horizon Model

8.5.1 fixes the plan/workflow stack around work horizons. The model is about work size, artifact altitude, and state lifetime, not calendar duration alone.

```text
one-shot
-> task_ticket
-> short_plan
-> long_plan

loop_overlay and support_facets can attach to any level when their trigger is explicit.
```

## Horizon Levels

| level | meaning | primary owner | durable state |
| --- | --- | --- | --- |
| `one_shot` | one response, one small edit, or one obvious command/check | task-specific direct execution | none by default |
| `task_ticket` | 3-5 shot work where findings/evidence can be lost across turns | task-specific primary plus `workflow-task-ledger` | `TaskRun`; optional `WorkItem` envelope |
| `short_plan` | current execution horizon; several task/ticket items in one tactical design | `plan-short-term-docs` | persisted `docs/plan` artifact |
| `long_plan` | multi-horizon phase/package/architecture plan | `plan-long-term-package` | planning package |
| `loop_overlay` | verifier-feedback convergence contract or execution | `plan-loop-term`, then `workflow-loop-runner` | LoopRun only after an accepted contract |
| `cross_horizon` | modifier, curation, recovery, validation, or execution behavior that can attach across levels | owning facet skill | depends on the owner |

## Planning Altitude

Plan skills are separated by artifact altitude:

| planning_altitude | owner | role |
| --- | --- | --- |
| `tactical_design` | `plan-short-term-docs` | executable short-plan artifact |
| `strategic_package` | `plan-long-term-package` | phase/package/architecture decomposition |
| `loop_contract` | `plan-loop-term` | success, verifier, retry, stop, and governance contract |
| `lifecycle_curation` | `plan-spec-curator` | closeout, archive load policy, active context pruning |

`short-term` means current execution horizon. In agentic development that commonly compresses to a 4-8 hour design/implementation/validation unit, even if the legacy human equivalent was one or two sprints.

`long-term` means multi-horizon architecture or phase package. In agentic development that can compress to two or three weeks, but it still governs multiple short plans.

## Execution Mode

Workflow skills are separated by how they control execution:

| execution_mode | owner | role |
| --- | --- | --- |
| `implementation_execution` | `workflow-implementation` | own direct coding and refactoring from requirement to validated diff |
| `bug_fix_execution` | `workflow-bug-fix` | own concrete failure repair from failure signal to verified fix |
| `dependency_upgrade_execution` | `workflow-dependency-upgrade` | own dependency/runtime/package upgrades and compatibility validation |
| `safe_refactor_execution` | `workflow-refactor-safely` | own behavior-preserving refactors with characterization checks |
| `plan_batch_execution` | `workflow-plan-runner` | execute an approved plan/spec/package in batches |
| `loop_convergence_execution` | `workflow-loop-runner` | run an accepted loop contract through verifier feedback |
| `checkpoint_ledger` | `workflow-task-ledger` | preserve task/ticket steps, findings, and evidence |
| `rigor_modifier` | `workflow-rigor` | evidence-first execution discipline |
| `recovery_intervention` | `workflow-recovery` | take over when repeated failure requires a changed strategy |
| `validation_lane` | `workflow-validation` | validation-only lane or attached check strategy |
| `minimality_constraint` | `workflow-minimal-implementation` | keep implementation minimal and dependency-light |

## Decision Table

| user intent | route |
| --- | --- |
| "작은 오타 하나만 고쳐" | direct one-shot execution; no ledger or plan |
| "이 기능 구현해줘" | `workflow-implementation`; attach rigor/minimality/validation only when triggered |
| "이 failing test 고쳐줘" | `workflow-bug-fix`; escalate to `workflow-recovery` if the same signature repeats |
| "React 버전 올리고 깨지는 call site까지 고쳐줘" | `workflow-dependency-upgrade` |
| "동작 보존하면서 모듈을 나눠줘" | `workflow-refactor-safely` |
| "다음 세션에도 이어갈 수 있게 상태를 남겨" | task-specific primary plus `workflow-task-ledger` |
| "이 작업을 플랜 문서로 만들어" | `plan-short-term-docs` |
| "이 migration을 phase package로 나눠" | `plan-long-term-package` |
| "이 goal을 반복 실행하기 전에 완료 조건을 잡아" | `plan-loop-term` |
| "승인된 loop contract를 실행해" | `workflow-loop-runner` |
| "이 plan대로 구현해" | `workflow-plan-runner`; attach `workflow-task-ledger` only when batch state must survive turns |
| "오래된 plan/spec을 정리하고 active context를 줄여" | `plan-spec-curator` |

## WorkItem And TaskRun

`WorkItem` is the lifecycle envelope: source, owner, state, evidence, findings, and next action.

`TaskRun` is the execution memory: steps, findings, observed evidence refs, and final verification.

Do not replace `workflow-task-ledger` with WorkItem. WorkItem tracks the ticket envelope; TaskRun tracks the actual multi-turn execution state.

Do not turn WorkItem into a queue runtime, scheduler, Kanboard source of truth, autonomous worker, or LoopRun replacement.
