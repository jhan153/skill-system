# Work Horizon Model

This model separates work size, artifact altitude, and state lifetime. Calendar duration alone does
not select a horizon.

```text
one-shot
-> task_ticket
-> long_plan

support_facets can attach to any level when their trigger is explicit.
```

## Question Ownership And Non-Executing Topology

This model owns work size, persistence, and artifact altitude. It does not select a domain specialist, admit a planning-state transition, or invoke a workflow chain.

| question | authority |
| --- | --- |
| Who owns the current turn? | The host `context-routing.md` and the selected direct specialist. |
| Does the work need durable task or plan state? | This Work Horizon Model. |
| May a persisted planning artifact move to its next state? | `planning_state_model.md`. |
| What durable state owns resumable execution? | The canonical Plan/Handoff pair selected for that horizon. |

For an explicit “what next?” question, choose only the first boundary that changes the actual deliverable or state lifetime:

1. If the target outcome is nameable but unresolved decisions and their dependencies need durable multi-session state, use explicit `plan-decision-map`. Otherwise, if an existing capability's next user path is blocked by a product-facing behavior decision, use behavior discovery; use requirements discovery for missing product, scope, edge, or data decisions. Use `plan-question-document` only when an explicit one-recipient input artifact is needed. Distill a durable contract only when that artifact is needed.
2. If requirements are stable and no persisted plan, resume boundary, transfer, or verifier-steered repetition is requested, keep the current task owner. Execute directly only when the current request authorizes mutation; a read-only “what next?” request receives a recommendation without starting work.
3. If unresolved decisions need durable state, use `plan-decision-map`; if execution needs durable state, use `plan-execution-handoff`. Requirements admission remains governed by the Planning State Model.
4. If one task must resume across turns, use `plan-execution-handoff` with `single_node_execution`; if ownership itself transfers without durable execution state, use an explicit lightweight handoff instead.
5. If durable execution is explicitly verifier-steered, apply the conditional `repeated_work_profile` while authoring its Execution Handoff DAG. A `/goal`, event runtime, task length, or governance risk alone does not activate that profile.

This is explanatory topology, not an orchestrator. It never calls the listed owners, requires every task to traverse every step, or overrides the current task owner.

## Horizon Levels

| level | meaning | primary owner | durable state |
| --- | --- | --- | --- |
| `one_shot` | one response, one small edit/command/check, or one bounded decision question | task-specific direct execution or discovery owner | none by default |
| `task_ticket` | one task whose findings/evidence must survive turns | `plan-execution-handoff` with `single_node_execution`; task-specific Workflow owns the executable node | canonical Plan/Handoff pair |
| `long_plan` | durable multi-horizon decision state or governed multi-session implementation DAG | `plan-decision-map` while material decisions remain; `plan-execution-handoff` after the implementation outcome and lifecycle are selected | decision map or canonical Plan/Handoff pair |
| `cross_horizon` | modifier, curation, validation, or execution behavior that can attach across levels | owning facet skill | depends on the owner |

## Planning Altitude

Plan skills are separated by artifact altitude:

| planning_altitude | owner | role |
| --- | --- | --- |
| `behavior_discovery` | `plan-behavior-discovery` | evidence-grounded product behavior decisions for the next slice of an existing capability |
| `requirements_discovery` | `plan-requirements-discovery` | human-in-loop elicitation before PRD/HLD/LLD planning |
| `requirements_discovery` | `plan-question-document` | explicit question document for one answer owner; returned answers are not implied |
| `requirements_contract` | `plan-requirements-brief` | PRD/SRS-lite requirements contract from discovery notes and decisions |
| `test_discovery` | `plan-test-discovery` | conditional human-owned test-basis/oracle decision record surfaced by Test Design and consumable through Execution Handoff revision |
| `strategic_decision_map` | `plan-decision-map` | durable target/decision map for unresolved multi-session dependencies before implementation decomposition |
| `durable_execution_handoff` | `plan-execution-handoff` | governed Plan/Handoff pair with one typed execution DAG and human boundary |
| `repeated_work_profile` | `plan-execution-handoff` | verifier-steering admission, condition/verifier terms, and evidence-delta expansion/stop rules compiled into an already-needed durable DAG |

Each `behavior_discovery`, `test_discovery`, or requirements ready-question round is a bounded
`one_shot` turn. A `plan-question-document` file is a one-shot answer request, not a discovery
result. A conversation may continue through another explicit round without creating a persisted
execution plan; use `task_ticket` only when one task genuinely needs durable resume state.
`plan-decision-map` is durable `long_plan` context but remains a decision map rather than an
implementation plan. Behavior/Test Discovery does not reopen requirements discovery or authorize
implementation. A requirements contract or decided test-discovery scope is input to direct work or
Execution Handoff, not an implementation plan by itself.

Use `planning_state_model.md` when a planning artifact might move between lifecycle states. Work horizon answers "how large and durable is this work?"; Planning State answers "which event and invariant admit this artifact into the next state?"

`long_plan` means a decision map or execution pair whose state must survive the current turn. It is
selected by persistence and dependency needs, not calendar duration.

## Reporting Altitude

Report skills may package artifacts across horizons without owning the underlying planning or execution:

| reporting_altitude | owner | role |
| --- | --- | --- |
| `implementation_explanation` | `report-implementation-explainer` | source/runtime-anchored implementation navigation, changed-line comparison, and productization-gap artifact for a concrete next decision |
| `lifecycle_artifact_reporting` | `report-lifecycle-artifacts` | Markdown index and traceability matrix over explicitly selected existing lifecycle artifacts; optional matching HTML view |

## Execution Mode

Workflow skills are separated by how they control execution:

| execution_mode | owner | role |
| --- | --- | --- |
| `implementation_execution` | `workflow-implementation` | own direct coding and refactoring from requirement to validated diff |
| `test_design_execution` | `workflow-test-design` | own one implementation-ready test contract after an executable SUT exists, including conditional human Test Discovery without test-code writes |
| `test_implementation_execution` | `workflow-test-implementation` | own bounded test-only assets and condition-scoped execution without changing the accepted oracle or production code |
| `runtime_debugging_execution` | `workflow-runtime-debugging` | own one execution-ready debugging scope or one approved debugger/dump/dynamic/graphics operation; return a direct or Core diagnostic result with safe session handback and no source repair or successor selection |
| `bug_fix_execution` | `workflow-bug-fix` | own one semantically admitted contract-preserving DAG intervention/result, or a bounded standalone repair under the same already-implemented accepted contract |
| `prototype_execution` | `workflow-prototype` | build and preserve one isolated runnable discriminator for a selected UI question or one self-contained offline HTML state/logic model through decision-owner observation, then stop before production hardening |
| `dependency_upgrade_execution` | `workflow-dependency-upgrade` | own dependency/runtime/package upgrades and compatibility validation |
| `source_maintenance_execution` | `workflow-source-maintenance` | own post-development source cleanup/dead-code pruning in `source_prune` mode or behavior-preserving comment/docstring/TODO-FIXME sync in `comment_sync` mode |
| `safe_refactor_execution` | `workflow-refactor-safely` | own behavior-preserving refactors with characterization checks |

Execution assurance is a conditional shared contract, not an execution mode, skill, or DAG node.
The active owner loads its local `references/execution_assurance_contract.md` only when standard or
strict maker-checker separation or rollback/readback is material.

## Decision Table

| user intent | route |
| --- | --- |
| "작은 오타 하나만 고쳐" | direct one-shot execution; no ledger or plan |
| "이 기능 구현해줘" | `workflow-implementation`; its directness rules remain active, and the execution-assurance contract applies only when medium/high risk or maker/checker separation is material |
| "이미 구현된 승인 동작의 이 failing test 결함을 고쳐줘" | `workflow-bug-fix`; the work-kind gate must confirm a bounded same-contract repair, then without Plan node fields use bounded standalone mode, while an assigned DAG `BF1/BF2` returns after exactly one round for Code Review/Coordinator consumption |
| "이 failing test가 요구하는 승인된 새 알고리즘을 처음 구현해줘" | `workflow-implementation`; the failing condition is evidence and does not turn first implementation into Bug Fix |
| "디버거는 아직 없지만 이 크래시를 어떻게 조사할지 범위를 잡아줘" | `workflow-runtime-debugging` in `scope` mode; return an execution-ready debugging contract with `causal_status: not_run` |
| "이미 멈춘 디버거에서 원인을 직접 좁혀줘" | `workflow-runtime-debugging` in `operate` mode; preserve target/artifact identity, debugger effects, proof ceiling, and safe session handback |
| "검색 결과 배치를 결정할 수 있게 구조가 다른 프로토타입 3개를 만들어줘" | `workflow-prototype`; keep the comparison throwaway and hand a selected result to production implementation separately |
| "React 버전 올리고 깨지는 call site까지 고쳐줘" | `workflow-dependency-upgrade` |
| "1차 개발 끝났으니 죽은 코드 지우고 소스 정리해줘" | `workflow-source-maintenance` |
| "주석이 코드랑 안 맞으니 최신화하고 불필요한 주석 정리해줘" | `workflow-source-maintenance` in `comment_sync` mode |
| "동작 보존하면서 모듈을 나눠줘" | `workflow-refactor-safely` |
| "다음 세션에도 이어갈 수 있게 상태를 남겨" | `plan-execution-handoff` with `single_node_execution` |
| "여러 세션이 필요한데 목적지만 보이고 결정 경로는 아직 흐려" | explicit `plan-decision-map`; create a decision map, not an implementation backlog |
| "구현 전에 요구사항 의존성을 보고 지금 답할 수 있는 것부터 질문해줘" | `plan-requirements-discovery`; ask a bounded round of mutually independent ready questions |
| "보안 책임자에게 비동기로 받을 질문 문서를 만들어줘" | explicit `plan-question-document`; create one local Markdown artifact and do not send it |
| "구현된 mesh 연산을 실제로 어떻게 preview/commit/undo할지 하나씩 결정하자" | `plan-behavior-discovery` |
| "인터뷰 결과를 PRD/요구사항 계약으로 정리해줘" | `plan-requirements-brief` |
| "이 작업을 지속 실행 플랜으로 만들어" | `plan-execution-handoff`; use `single_node_execution` when only one executable node is needed |
| "이 migration을 여러 세션이 실행할 Plan/Handoff DAG로 나눠" | `plan-execution-handoff` |
| "요구사항부터 QA/보안/릴리즈까지 SDLC 산출물 패키지로 만들어줘" | `report-lifecycle-artifacts` |
| "구현된 알고리즘을 소스와 trace 기반 HTML 코드리뷰로 설명해줘" | `report-implementation-explainer` |
| "이 goal을 반복 실행하기 전에 완료 조건을 잡아" | `plan-execution-handoff` with conditional repeated-work principles |
| "승인된 verifier-steered Plan/Handoff를 실행해" | the Orchestrator follows the bounded DAG copied into the accepted pair |
| "이 plan대로 구현해" | follow an existing canonical Plan/Handoff, or route one bounded approved slice to its task-specific Workflow |
| "오래된 plan/spec을 정리하고 active context를 줄여" | current task owner with the exact named files; no persistent planning owner is activated |
