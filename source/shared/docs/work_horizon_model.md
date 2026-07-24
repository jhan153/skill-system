# Work Horizon Model

8.5.1 fixes the plan/workflow stack around work horizons. The model is about work size, artifact altitude, and state lifetime, not calendar duration alone.

```text
one-shot
-> task_ticket
-> short_plan
-> long_plan

loop_overlay and support_facets can attach to any level when their trigger is explicit.
```

## Question Ownership And Non-Executing Topology

This model owns work size, persistence, and artifact altitude. It does not select a domain specialist, admit a planning-state transition, or invoke a workflow chain.

| question | authority |
| --- | --- |
| Who owns the current turn? | The host `context-routing.md` and the selected direct specialist. |
| Does the work need durable task or plan state? | This Work Horizon Model. |
| May a persisted planning artifact move to its next state? | `planning_state_model.md`. |
| What lifecycle state does a ticket envelope have? | `work_item_lifecycle.md`. |

For an explicit “what next?” question, choose only the first boundary that changes the actual deliverable or state lifetime:

1. If an existing capability's next user path is blocked by a product-facing behavior decision, use behavior discovery; otherwise use requirements discovery for missing product, scope, edge, or data decisions. Distill a durable contract only when that artifact is needed.
2. If requirements are stable and no persisted plan, resume boundary, transfer, or loop is requested, keep the current task owner. Execute directly only when the current request authorizes mutation; a read-only “what next?” request receives a recommendation without starting work.
3. If durable current-horizon or strategic planning is explicitly needed, select `short_plan` or `long_plan`; use the Planning State Model for its transition into execution.
4. If one task must resume across turns, attach `task_ticket`; if ownership itself transfers, use an explicit handoff instead. Neither condition creates a plan automatically.
5. If execution is explicitly repeated, event-driven, `/goal`, or verifier-feedback based, evaluate `loop_overlay`; it runs only after its own accepted contract.

This is explanatory topology, not an orchestrator. It never calls the listed owners, requires every task to traverse every step, or overrides the current task owner.

## Horizon Levels

| level | meaning | primary owner | durable state |
| --- | --- | --- | --- |
| `one_shot` | one response, one small edit/command/check, or one bounded decision question | task-specific direct execution or discovery owner | none by default |
| `task_ticket` | 3-5 shot work where findings/evidence can be lost across turns | task-specific primary plus `workflow-task-ledger` | `TaskRun`; optional `WorkItem` envelope |
| `short_plan` | current execution horizon; several task/ticket items in one tactical design | `plan-short-term-docs` | persisted `docs/plan` artifact |
| `long_plan` | multi-horizon phase/package/architecture plan | `plan-long-term-package` | planning package |
| `loop_overlay` | verifier-feedback convergence contract or execution | `plan-loop-term`, then `workflow-loop-runner` | LoopRun only after an accepted contract |
| `cross_horizon` | modifier, curation, recovery, validation, or execution behavior that can attach across levels | owning facet skill | depends on the owner |

## Planning Altitude

Plan skills are separated by artifact altitude:

| planning_altitude | owner | role |
| --- | --- | --- |
| `behavior_discovery` | `plan-behavior-discovery` | evidence-grounded product behavior decisions for the next slice of an existing capability |
| `requirements_discovery` | `plan-requirements-discovery` | human-in-loop elicitation before PRD/HLD/LLD planning |
| `requirements_contract` | `plan-requirements-brief` | PRD/SRS-lite requirements contract from discovery notes and decisions |
| `tactical_design` | `plan-short-term-docs` | executable short-plan artifact |
| `strategic_package` | `plan-long-term-package` | phase/package/architecture decomposition |
| `loop_contract` | `plan-loop-term` | success, verifier, retry, stop, and governance contract |
| `lifecycle_curation` | `plan-spec-curator` | closeout, archive load policy, active context pruning |

Each `behavior_discovery` or `requirements_discovery` question is a non-persisted `one_shot` turn. A conversation may continue through another explicit question without becoming a `short_plan`; attach `task_ticket` only when the user requests durable cross-turn resumption and persist a discovery record only on explicit request. `behavior_discovery` does not reopen requirements discovery or authorize implementation. `requirements_discovery` and `requirements_contract` sit before tactical and strategic planning. None is an implementation plan by itself.

Use `planning_state_model.md` when a planning artifact might move between lifecycle states. Work horizon answers "how large and durable is this work?"; Planning State answers "which event and invariant admit this artifact into the next state?"

`short-term` means current execution horizon. In agentic development that commonly compresses to a 4-8 hour design/implementation/validation unit, even if the legacy human equivalent was one or two sprints.

`long-term` means multi-horizon architecture or phase package. In agentic development that can compress to two or three weeks, but it still governs multiple short plans.

## Reporting Altitude

Report skills may package artifacts across horizons without owning the underlying planning or execution:

| reporting_altitude | owner | role |
| --- | --- | --- |
| `implementation_explanation` | `report-implementation-explainer` | source/runtime-anchored implementation navigation and productization-gap artifact for a concrete next decision |
| `lifecycle_artifact_reporting` | `report-lifecycle-artifacts` | SDLC/product lifecycle artifact pack and traceability matrix from planning, implementation, validation, security, release, and retrospective evidence |

## Execution Mode

Workflow skills are separated by how they control execution:

| execution_mode | owner | role |
| --- | --- | --- |
| `implementation_execution` | `workflow-implementation` | own direct coding and refactoring from requirement to validated diff |
| `bug_fix_execution` | `workflow-bug-fix` | own concrete failure repair from failure signal to verified fix |
| `comment_maintenance_execution` | `workflow-comment-maintenance` | own behavior-preserving comment/docstring/TODO-FIXME sync to current code meaning |
| `dependency_upgrade_execution` | `workflow-dependency-upgrade` | own dependency/runtime/package upgrades and compatibility validation |
| `source_maintenance_execution` | `workflow-source-maintenance` | own post-development source cleanup and evidence-gated dead-code pruning |
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
| "1차 개발 끝났으니 죽은 코드 지우고 소스 정리해줘" | `workflow-source-maintenance` |
| "주석이 코드랑 안 맞으니 최신화하고 불필요한 주석 정리해줘" | `workflow-comment-maintenance` |
| "동작 보존하면서 모듈을 나눠줘" | `workflow-refactor-safely` |
| "다음 세션에도 이어갈 수 있게 상태를 남겨" | task-specific primary plus `workflow-task-ledger` |
| "구현 전에 요구사항을 하나씩 질문해서 끌어내줘" | `plan-requirements-discovery` |
| "구현된 mesh 연산을 실제로 어떻게 preview/commit/undo할지 하나씩 결정하자" | `plan-behavior-discovery` |
| "인터뷰 결과를 PRD/요구사항 계약으로 정리해줘" | `plan-requirements-brief` |
| "이 작업을 플랜 문서로 만들어" | `plan-short-term-docs` |
| "이 migration을 phase package로 나눠" | `plan-long-term-package` |
| "요구사항부터 QA/보안/릴리즈까지 SDLC 산출물 패키지로 만들어줘" | `report-lifecycle-artifacts` |
| "구현된 알고리즘을 소스와 trace 기반 HTML 코드리뷰로 설명해줘" | `report-implementation-explainer` |
| "이 goal을 반복 실행하기 전에 완료 조건을 잡아" | `plan-loop-term` |
| "승인된 loop contract를 실행해" | `workflow-loop-runner` |
| "이 plan대로 구현해" | `workflow-plan-runner`; attach `workflow-task-ledger` only when batch state must survive turns |
| "오래된 plan/spec을 정리하고 active context를 줄여" | `plan-spec-curator` |

## WorkItem And TaskRun

`WorkItem` is the lifecycle envelope: source, owner, state, evidence, findings, and next action.

`TaskRun` is the execution memory: steps, findings, observed evidence refs, and final verification.

Do not replace `workflow-task-ledger` with WorkItem. WorkItem tracks the ticket envelope; TaskRun tracks the actual multi-turn execution state.

Do not turn WorkItem into a queue runtime, scheduler, Kanboard source of truth, autonomous worker, or LoopRun replacement.
