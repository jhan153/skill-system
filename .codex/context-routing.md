# Context Routing

This file is the operational routing reference for the global `.codex` setup. Keep `AGENTS.md` thin; put route details, conflict rules, and audit contracts here.

## Custom Skill Scope
`.codex/skills/.system` is a Codex app-managed namespace. Custom skill lifecycle operations apply only to user-managed skills under `.codex/skills/*` excluding `.system`. Do not audit, patch, migrate, deprecate, route-register, or smoke-test `.system` skills through `create-skill-pack`.

## Mode Separation
Development / Implementation Mode:
- Use for coding, refactoring, bug fixing, implementation plans, repo work, tests, scripts, APIs, build/lint/test tasks.
- Treat user-provided requirements, keywords, file names, APIs, metrics, and implementation constraints as task specifications unless they are ambiguous, impossible, unsafe, contradictory, or conflict with repo rules.
- Do not perform broad premise skepticism by default.
- Do not route to `research-hypothesis-planning` just because the user mentions "experiment", "approach", "model", "loss", or "metric" in a development context.
- Prefer concrete execution, verification, and repo validation.
- Direct implementation commands such as `구현해`, `작업해`, `플랜대로 구현`, `fix`, `add tests`, or `refactor` stay in Development / Implementation Mode even when an active plan document exists.
- Active plans may be read as task input and updated as secondary status tracking, but they must not replace source, test, runtime config/build, or executable scaffold changes for implementation requests.
- Markdown-only, plan-only, spec-only, report-only, memory-only, or planning-manifest-only diffs are not implementation completion unless the user explicitly requested documentation/spec work only.
- If a requested implementation cannot produce a non-documentation implementation diff, report `blocked` or analysis-only with the exact blocker instead of claiming completion.

Research Hypothesis Planning Mode:
- Use only when the user explicitly asks for research plan, paper idea, novel method, experiment design, ablation design, loss design, training plan, hypothesis planning, or scientific claim development.
- Treat user-provided causal or field-state claims as hypotheses, not facts.
- Use premise triage, checkpoint-first baseline, one-claim core experiment, progressive ablation, and loss budget.

If the request is primarily about implementing an already chosen method, stay in Development / Implementation Mode. If the request is primarily about deciding whether a scientific claim/method is valid or publishable, use Research Hypothesis Planning Mode.

## Context Bundle Contract
The context bundle is internal by default. Surface it only when the user asks for routing rationale or when work is complex, risky, write-producing, report-producing, or memory-mutating.

```yaml
context_bundle:
  primary_skill: null
  modifiers: []
  review_gate: null
  output_modifier: null
  memory_operation: null
  knowledge_context:
    mode: none
    anchors:
      files: []
      components: []
      topics: []
      decisions: []
      kanboard_cards: []
    claim_types: []
    relation_types: []
    max_hops: 1
    raw_verify: on_conflict
  must_read: []
  read_if_needed: []
  do_not_load_by_default: []
  risk_gates: []
  validation_context: []
  expansion_policy: one_layer_at_a_time
```

Build this bundle before multi-step work, writes, broad scans, reports, automation changes, or memory mutation. If information is missing, expand only from `read_if_needed`, one layer at a time. Never recover by loading all repo docs, all memory, all skills, or full chat history.

## Skill Precedence
1. Explicit user invocation of a skill alias wins.
2. Explicit artifact intent wins over generic analysis.
3. Heavy artifact generators require explicit artifact, package, or report intent.
4. Primary skills own task execution.
5. Router skills may choose a primary skill but must not perform writes.
6. Execution modifiers attach only when implementation or medium/high-risk change is active.
7. Output modifiers attach only to final presentation.
8. Review gates attach only when critical review, QA, blocker, risk, or validation is requested.
9. Memory operations attach only when persistent memory mutation or inspection is explicit.
10. If two skills could apply, choose the narrower one and mark the broader one as excluded.

## Route Matrix
| Request type | Primary skill | Optional attachment | Must read | Default exclude |
| --- | --- | --- | --- | --- |
| bug diagnosis | `analysis-router` -> `analysis-bug` | `workflow-rigor` only if implementation/risk is active | symptom, repro, relevant files, logs | full repo report |
| bug fix implementation | `workflow-bug-fix` | `analysis-bug` for unclear RCA; `workflow-recovery` for repeated same-signature failure; `workflow-validation` for check redesign when installed or explicitly requested; `workflow-rigor` for risky fixes | failure signal, expected behavior, repro or failing command, target files/tests | full repo report, plan package, broad redesign |
| algorithm proposal | `analysis-router` -> `analysis-algorithm` | `report-qualitative` only for formal output | constraints, metrics, candidates | full repo or memory |
| domain modeling for development | `analysis-domain-modeling` | `workflow-refactor-safely` or `workflow-implementation` only after a model decision is selected | domain area, current terminology, source/schema/tests/docs with domain rules | persistent memory/docs mutation, pure product ideation, module-boundary-only design |
| performance analysis | `analysis-performance` | `workflow-implementation` only after a bottleneck and optimization are selected; `workflow-validation` for measurement plan when installed or explicitly requested | performance symptom, metric/workload, baseline or profile/log gap, hot path | correctness bug workflow, repo-wide report, research benchmark planning |
| research / scientific workflow | `research-router` | selected narrow research cluster skill; `plan-short-term-docs` only for explicit persisted `docs/plan` artifact | research request, stage hints, provided artifacts, `.codex/research-routing.md` when needed | full repo, full memory bank, `analysis-codebase`, `plan-long-term-package`, experiment scaffold unless explicitly requested |
| cross-domain evidence search | `search-router` | selected evidence lane such as `search-paper-evidence`, `analysis-bug`, `design-visual-regression`, `memory-bank-harness`, `knowledge-context-harness`, or `search-deep-evidence` for a deep multi-angle adversarially-verified sweep | evidence intent, domain hint, claim/topic, final task owner | final synthesis, implementation, broad research lifecycle |
| loop readiness classification | `loop-readiness-router` | `plan-loop-term` only after `contract_needed` or `loop_worthy`; `workflow-loop-runner` only after accepted contract | prompt draft, target domain, verifier hints, side-effect, approval, durability, event-runtime, Wiki feedback, parallelism, and idempotency signals | direct execution, contract drafting, verifier execution, broad planning |
| loop verifier mapping | `loop-verifier-registry` | `plan-loop-term` when embedding map into a contract; verifier skills only as owners, not executors | loop term or success conditions, verifier catalog, target domain, governance metrics | running checks, implementation, readiness classification |
| accepted loop contract execution | `workflow-loop-runner` | task-specific primary skill; `workflow-recovery` for repeated failures; `workflow-validation` for verifier strategy; `knowledge-base-maintenance` only for explicit Wiki feedback review | accepted loop term, verifier map, governance gates, loop budget, checkpoint state, approval gates | contract creation, readiness classification, one-shot work, accepted Wiki mutation |
| implementation | `workflow-implementation` | `workflow-minimal-implementation` only for explicit YAGNI/minimality requests or credible over-engineering pressure; `workflow-rigor` for medium/high-risk changes; `workflow-validation` for check selection when installed or explicitly requested; `plan-short-term-docs` only as secondary status sync when an active plan is explicitly in scope | repo `AGENTS.md`, relevant files, active plan as input when explicitly referenced, validation | unrelated docs, plan-only completion |
| dependency upgrade | `workflow-dependency-upgrade` | `workflow-rigor` for risky upgrades; `workflow-validation` for compatibility matrix when installed or explicitly requested; `workflow-recovery` for repeated upgrade failure | package/runtime manifests, lockfiles, target dependency/version, usage sites, validation | broad package churn, unrelated feature work, security verdict-only review |
| post-development source maintenance | `workflow-source-maintenance` | `workflow-validation` for deletion/build/typecheck/test check selection; `workflow-minimal-implementation` only as YAGNI pressure; `workflow-refactor-safely` only when cleanup uncovers structural refactor work | maintenance scope, target source/callers/tests, public exports, dynamic entrypoint risks, validation command | feature changes, concrete bug fixes, broad architecture redesign, dependency upgrades, comment-only edits |
| comment-only maintenance | `workflow-comment-maintenance` | `workflow-validation` for doc-build/docstring-lint/typecheck check selection; `workflow-source-maintenance` only when comment work uncovers dead-code cleanup; `workflow-implementation` / `workflow-refactor-safely` only when a comment exposes a needed behavior or structure change | comment scope, target source and the described code, public/framework docstring consumption, validation command | feature changes, bug fixes, structural refactors, dead-code cleanup, dependency upgrades, README/wiki documentation writing |
| behavior-preserving refactor | `workflow-refactor-safely` | `analysis-codebase-design` before boundary changes; `workflow-minimal-implementation` for abstraction pressure; `workflow-validation` for characterization checks when installed or explicitly requested | refactor goal, behavior contract, target files/callers, tests or smoke command | feature changes, bug fixes, design-only analysis, broad rewrite |
| approved plan/spec execution | `workflow-plan-runner` | `workflow-rigor` for execution discipline; `workflow-validation` for check selection; `coordination-*` only for explicit handoff or multi-agent ownership | approved plan/spec/package slice, target phase or batch, execution-source sufficiency, source/test/config files, validation contract | plan/spec creation, plan-only completion, all plan packages |
| validation-only work | `workflow-validation` | `workflow-rigor` only when validation itself has medium/high risk | changed artifact or plan/spec slice, success criteria, risk tier, available checks | `evaluation-harness`, broad repo audit, critical verdicts |
| repeated failure recovery | `workflow-recovery` | `analysis-bug` for deeper RCA; `workflow-validation` for check redesign; `workflow-rigor` for risky fixes | repeated failure signature, failing command/log, latest attempted fix, narrowed repro, target files | broad redesign, plan package, simple rerun |
| plan document | `plan-short-term-docs` | `report-critical` only for QA/review | active plan, plan template | phase package |
| goal/loop term contract | `plan-loop-term` | `loop-readiness-router` if readiness is unknown; `loop-verifier-registry` if verifier ownership is unclear; `plan-short-term-docs` only when persisting into `docs/plan`; `plan-long-term-package` only when this is one artifact in a broad phase package | goal or loop intent, target plan/spec, success criteria, verifier evidence, governance coverage, budgets, stop/retry boundaries | implementation, loop execution, broad package ownership, generic validation-only work |
| context/spec lifecycle curation | `plan-spec-curator` | `report-critical` only for QA/review | current goal or task, candidate plan/spec slice, lifecycle state when available | full memory bank, all old plans, archived raw plans, full chat history |
| knowledge context consumption | owning task primary | `knowledge-context-harness` only when `knowledge_context.mode` is `optional` or `required` | generated Runtime Projection index/cards, selected Context Pack, validation command | full Wiki Bank, raw chat, all plans, accepted knowledge mutation |
| knowledge maintenance | `knowledge-base-maintenance` | `workflow-rigor` for write validation | target Knowledge Store files, feedback packet or claim IDs, projection validation | Memory Bank mutation, hooks as accepted knowledge, unrelated projections |
| phase package | `plan-long-term-package` | `workflow-rigor` if execution risk is active | prior reports, templates | lightweight plan only |
| codebase design / deep module analysis | `analysis-codebase-design` for one boundary decision or `analysis-architecture-deepening` for ranked candidates | `workflow-minimal-implementation` as abstraction pressure; `workflow-implementation` only after a candidate is selected | design pressure, target modules/call sites/tests, local patterns | full repo report, direct implementation before selection, domain glossary-only work |
| codebase report | `analysis-codebase` | `report-critical` after report if requested | repo root, scripts, tracked files | single-bug workflow |
| qualitative evaluation report | `report-qualitative` | `report-critical` only if blocker/QA verdict is also requested | artifact slice, evaluation goal, audience, criteria, evidence anchors, redaction boundary | readable changed-line diffs, artifact inventory, eval telemetry, implementation, debugging |
| diff presentation | `report-diff` | `report-critical` only if verdict requested | verified diff or snapshot | root-cause workflow |
| critical review | `report-critical` | `report-qualitative` if formal report requested | artifact slice, goal, evidence anchors | full history |
| memory operation | `memory-bank-init`, `memory-bank-update`, `memory-bank-correction-capture`, or `memory-bank-maintenance` | none by default | matching active memory cards and target memory files | unrelated memory |
| skill lifecycle | `create-skill-pack` for user-managed custom skills under `.codex/skills/*` excluding `.system` | `report-critical` optional after draft | lifecycle request, target custom skill, one or two adjacent examples | `.system`, unrelated repo files, full skill library |

Development/implementation requests keep the existing implementation, bug, algorithm, or plan skills as primary and follow concrete user requirements as task specifications. Do not route to the research cluster merely because a development request mentions model, metric, experiment, loss, or training. Detailed Research Cluster routing lives in `.codex/research-routing.md`.

Knowledge context compilation does not imply Memory Bank mutation. Persistent Memory Bank mutation still requires explicit memory-bank workflows, and generated Wiki Bank / Runtime Projection artifacts must not be treated as editable memory state.

Aliases may remain in user-facing language, but routing docs should show actual skill IDs. Use system-provided `skill-creator` only when the runtime explicitly exposes it and the user asks for that platform-specific path; otherwise `create-skill-pack` owns user-managed custom `.codex` skill lifecycle work, including reference packs, hardening, migration, metadata, routing registration, smoke tests, and deprecation notes. `.system` skills are outside this lifecycle.

## Work Horizon Decision Table

Use `.codex/docs/work_horizon_model.md` as the detailed reference. The table below resolves plan/workflow ambiguity before selecting a primary skill.

| Horizon / intent | Primary route | Attachments | Exclude |
| --- | --- | --- | --- |
| direct one-shot edit/check | small direct execution or `workflow-implementation` when coding workflow is useful | none by default | `workflow-task-ledger`, `plan-short-term-docs`, `plan-loop-term`, `workflow-loop-runner` |
| task/ticket state across turns | task-specific primary such as `workflow-implementation` plus `workflow-task-ledger` | WorkItem only as lifecycle envelope when requested or already present | `plan-long-term-package`, `workflow-loop-runner` unless verifier feedback is required |
| tactical design/current execution plan | `plan-short-term-docs` | `workflow-validation` or `report-critical` only when requested | `plan-long-term-package` |
| strategic phase/package plan | `plan-long-term-package` | `plan-spec-curator` for lifecycle cleanup | `plan-short-term-docs` as primary |
| loop contract | `plan-loop-term` | `loop-verifier-registry` when verifier ownership is unclear | `workflow-loop-runner` before contract acceptance |
| approved plan execution | `workflow-plan-runner` | `workflow-task-ledger` only when batch state must survive turns; `workflow-validation` for checks | plan creation skills as primary |
| accepted loop execution | `workflow-loop-runner` | `workflow-recovery` for repeated failure; `workflow-task-ledger` only for adjacent non-loop task state | one-shot execution, plan creation |
| plan/spec/context lifecycle cleanup | `plan-spec-curator` | memory/knowledge workflows only with explicit mutation/review intent | implementation owners, full history loading |

## Design Cluster Routing

Design specialists are narrow. `design-frontend` remains the primary implementation owner for concrete visual artifacts. Evidence gates and analysis skills should not take over code changes unless the user explicitly asks for that kind of artifact.

| Request type | Primary skill | Supporting skill(s) | Must not trigger as primary |
| --- | --- | --- | --- |
| concrete visual artifact to repo UI code | `design-frontend` | token/component/visual/a11y gates when evidence exists | `design-ui-decomposer`, `design-layout-translator` |
| visual reference breakdown without code | `design-ui-decomposer` | `design-layout-translator` if constraints dominate | `design-frontend` |
| Auto Layout/flex/grid/sizing/overflow/breakpoint translation | `design-layout-translator` | `design-visual-regression` only after rendered evidence exists | `design-frontend` |
| explicitly invoked mobile/native screen implementation | `design-mobile-screen` | `design-frontend`, `design-visual-regression`, `design-a11y-audit` | `design-dashboard`, `design-section-web` |
| explicitly invoked dashboard/admin/analytics implementation | `design-dashboard` | `design-frontend`, `design-component-mapper`, `design-visual-regression`, `design-a11y-audit` | `design-mobile-screen`, `design-section-web` |
| explicitly invoked section-based web implementation | `design-section-web` | `design-frontend`, `design-visual-regression`, `design-a11y-audit` | `design-mobile-screen`, `design-dashboard` |
| token source normalization or token gaps | `design-tokens` | `design-component-mapper` if component styles are involved | `design-frontend` |
| design component to repo component/state mapping | `design-component-mapper` | `design-tokens`, `design-a11y-audit` when relevant | `design-visual-regression` |
| rendered screenshot, nonblank, viewport, or visual diff evidence | `design-visual-regression` | `design-a11y-audit` for focus/contrast/readability | `design-frontend` |
| keyboard/focus/semantic/contrast/target-size/readability evidence | `design-a11y-audit` | `design-visual-regression` for rendered screenshot evidence | `design-frontend` |

Design cluster conservative defaults:
- New or recently hardened design skills keep `allow_implicit_invocation: false` until route smoke tests and field feedback justify broader routing.
- `design-ui-decomposer` and `design-layout-translator` are operational `experimental` analysis skills, but should remain explicit or clearly analysis-intent routed until field feedback exists.
- Surface-specific implementation skills are active `experimental` explicit-only surface specialists; they do not auto-displace `design-frontend` for generic visual implementation.
- Each new design skill needs at least three `should_not_trigger` cases before implicit invocation can be reconsidered.

## Routing Card Audit Shape
Each user-managed custom `SKILL.md` Routing Card, excluding `.codex/skills/.system/**`, should keep these Markdown fields in this order unless a local reason exists: `role`, `intent_signature`, `use_when`, `do_not_use_when`, `expected_inputs`, `expected_outputs`, `context_targets` with `must_read`, `read_if_needed`, `do_not_load_by_default`, `risk_profile` with `reads`, `writes`, `tools`, `sensitive_resources`, and `entry_scene`.

## Route Smoke Tests
Use these examples as drift checks for routing behavior. They are not user-facing templates.

Schema meanings:
- `expected_primary_skill`: workflow that should own execution.
- `target_skill`: skill being inspected or modified; it may be read without owning execution.
- `exclude_as_primary_skill`: skills that may be read as targets but must not own execution.
- `must_not_route_to`: skills that should not be selected or attached.
- `expected_default_exclude`: context or workflows excluded by default.
- `expected_route_class`: use when no single primary skill is expected.

```yaml
route_smoke_tests:
  - request: "새 Codex 스킬 팩 만들어줘"
    expected_primary_skill: "create-skill-pack"
    expected_mode: "create_new_skill_pack"
    expected_attachments: []
    must_not_route_to:
      - "analysis-codebase"
      - "plan-long-term-package"
    notes: "Skill lifecycle creation, not repo-wide reporting or planning package generation."
  - request: "기존 analysis-bug 스킬의 Routing Card와 Risk Boundary를 보강해줘"
    expected_primary_skill: "create-skill-pack"
    expected_mode: "harden_existing_skill"
    target_skill: "analysis-bug"
    must_read:
      - "skills/analysis-bug/SKILL.md"
    exclude_as_primary_skill:
      - "analysis-bug"
    expected_attachments:
      - "report-critical optional after draft"
    notes: "This is skill lifecycle hardening, not bug analysis execution."
  - request: "스킬 말고 reference pack만 만들어줘"
    expected_primary_skill: "create-skill-pack"
    expected_mode: "create_reference_pack"
    expected_attachments: []
    expected_default_exclude:
      - "skills/{pack-name}/SKILL.md"
      - "skills/{pack-name}/agents/openai.yaml"
      - "context-routing.md route registration"
    must_not_route_to:
      - "memory-bank-init"
      - "memory-bank-update"
      - "memory-bank-correction-capture"
      - "memory-bank-maintenance"
      - "analysis-codebase"
    notes: "Reference-only packs prefer `.codex/references/{reference-pack-id}/` and are not route-registered as skills."
  - request: "스킬이란 개념이 뭐야?"
    expected_primary_skill: null
    expected_route_class: "conceptual_explanation"
    expected_attachments: []
    must_not_route_to:
      - "create-skill-pack"
    notes: "Conceptual explanation does not create or modify skill artifacts."
  - request: "analysis-bug로 이 버그 분석해줘"
    expected_primary_skill: "analysis-bug"
    expected_attachments: []
    must_not_route_to:
      - "create-skill-pack"
    notes: "Executing a skill is not creating or hardening a skill."
  - request: "최소 구현으로 이 기능 추가해줘. 새 의존성은 가능하면 피하고 과잉 추상화도 막아줘"
    expected_primary_skill: "task-specific primary"
    expected_attachments:
      - "workflow-minimal-implementation"
    must_not_route_to:
      - "create-skill-pack"
      - "analysis-codebase"
    notes: "Explicit minimal implementation pressure attaches the execution modifier; it is not a lifecycle or broad codebase analysis request."
  - request: "이 오래된 스킬을 deprecated 처리하고 새 스킬로 이동 경로를 정리해줘"
    expected_primary_skill: "create-skill-pack"
    expected_mode: "deprecate_skill"
    expected_attachments: []
    must_not_route_to:
      - "memory-bank-maintenance"
    notes: "Deprecation updates lifecycle notes and routing references; deletion requires explicit approval."
  - request: "방금 만든 스킬을 context-routing에 등록하고 smoke test도 추가해줘"
    expected_primary_skill: "create-skill-pack"
    expected_mode: "register_routing"
    expected_attachments: []
    must_read:
      - "context-routing.md"
    must_not_route_to:
      - "analysis-codebase"
    notes: "Routing registration and smoke tests are skill lifecycle work."
  - request: ".system 스킬도 Routing Card 보강해줘"
    expected_primary_skill: null
    expected_route_class: "out_of_scope_system_managed_skill"
    expected_attachments: []
    must_not_route_to:
      - "create-skill-pack"
    notes: "`.codex/skills/.system` is Codex app-managed and outside custom skill lifecycle scope."
  - request: "이 버그가 왜 반복되는지 원인 분석해줘"
    expected_primary_skill: "analysis-bug"
    expected_route_class: "routed_by_deep-analysis-workflow"
    expected_attachments: []
    must_not_route_to:
      - "analysis-codebase"
      - "plan-long-term-package"
    notes: "Bug diagnosis is point analysis, not repo-wide reporting."
  - request: "이 문제는 어떤 알고리즘/접근이 제일 맞아?"
    expected_primary_skill: "analysis-algorithm"
    expected_route_class: "routed_by_deep-analysis-workflow"
    expected_attachments: []
    must_not_route_to:
      - "analysis-codebase"
      - "memory-bank-init"
      - "memory-bank-update"
      - "memory-bank-correction-capture"
      - "memory-bank-maintenance"
    notes: "Recommendation intent selects the algorithm primary, not bug RCA."
  - request: "이 주장에 대한 논문, 코드, 런타임 근거 중 어떤 evidence lane을 타야 할지 먼저 골라줘"
    expected_primary_skill: "search-router"
    expected_route_class: "cross_domain_evidence_lane_selection"
    expected_attachments: []
    must_not_route_to:
      - "research-router"
      - "report-qualitative"
    notes: "Explicit evidence-lane selection belongs to search-router; it should not synthesize or report."
  - request: "이 구현을 검토하고 개선점 알려줘"
    expected_primary_skill: null
    expected_route_class: "ordinary_review_or_task_specific_primary"
    expected_attachments: []
    must_not_route_to:
      - "search-router"
    notes: "Bare review without evidence/source/proof intent must not use the evidence router."
  - request: "이 개념을 탐색해보자"
    expected_primary_skill: null
    expected_route_class: "casual_exploration"
    expected_attachments: []
    must_not_route_to:
      - "analysis-router"
    notes: "Casual exploration needs no deep-analysis router unless deep technical diagnosis or recommendation intent is present."
  - request: "이 작업을 docs/plan 플랜 문서로 만들어줘"
    expected_primary_skill: "plan-short-term-docs"
    expected_attachments: []
    must_not_route_to:
      - "plan-long-term-package"
    notes: "Persisted docs/plan artifact intent is explicit."
  - request: "/goal로 돌리기 전에 완료 조건, 검증 기준, 중단 조건 계약서만 만들어줘"
    expected_primary_skill: "plan-loop-term"
    expected_attachments: []
    must_not_route_to:
      - "workflow-plan-runner"
      - "workflow-validation"
      - "plan-long-term-package"
    notes: "Planning-stage goal/loop completion terms, not execution, post-change validation, or a broad phase package."
  - request: "버튼 색만 바꾸는 작업인데 루프로 돌릴 필요가 있는지 판단해줘"
    expected_primary_skill: "loop-readiness-router"
    expected_route_class: "loop_readiness_one_shot"
    expected_attachments: []
    must_not_route_to:
      - "plan-loop-term"
      - "workflow-loop-runner"
    notes: "Explicit readiness request, but simple deterministic UI tweak should classify one-shot with anti-loop signals and minimum sufficient path."
  - request: "이 Figma 화면을 맞을 때까지 구현하려고 해. 먼저 루프 준비 상태를 판정해줘"
    expected_primary_skill: "loop-readiness-router"
    expected_route_class: "loop_readiness_loop_worthy"
    expected_attachments:
      - "plan-loop-term if user proceeds"
      - "loop-verifier-registry if contract is drafted"
    must_not_route_to:
      - "workflow-loop-runner"
    notes: "Design fidelity plus repeated verifier feedback is loop-worthy, but execution waits for an accepted contract and verifier map."
  - request: "이 loop_term의 SC-DESIGN 조건들을 어떤 verifier skill이 봐야 하는지 매핑해줘"
    expected_primary_skill: "loop-verifier-registry"
    expected_attachments:
      - "plan-loop-term optional for embedding"
    must_not_route_to:
      - "workflow-loop-runner"
      - "design-frontend"
    notes: "Verifier mapping does not run implementation or checks; it names owner, independence, evidence, pass/fail signals, and unavailable labels."
  - request: "승인된 loop_term과 verifier_map 기준으로 반복 실행해줘"
    expected_primary_skill: "workflow-loop-runner"
    expected_attachments:
      - "task-specific primary"
      - "workflow-recovery on repeated failure"
    must_not_route_to:
      - "plan-loop-term"
      - "loop-readiness-router"
    notes: "Accepted loop contract execution belongs to workflow-loop-runner with observe-decide-act-verify-checkpoint state."
  - request: "이 루프는 배포 retry가 필요할 수도 있어. 비멱등 재시도와 stop hook 평가까지 계약에 넣어줘"
    expected_primary_skill: "plan-loop-term"
    expected_attachments:
      - "loop-verifier-registry if verifier ownership is unclear"
    must_not_route_to:
      - "workflow-loop-runner"
    notes: "Non-idempotent retry and Stop-hook loop evaluation are governance contract concerns before execution."
  - request: "현재 turn의 live agent-run run.yaml이 자동으로 시작되고 Stop 검증까지 이어지게 bootstrap을 추가해줘"
    expected_primary_skill: "task-specific implementation"
    expected_attachments:
      - "workflow-rigor for hook/runtime validation risk"
      - "workflow-task-ledger if this spans multiple dependent changes"
    must_read:
      - ".codex/docs/agent_output_validation.md"
      - ".codex/hooks/codex_hook_adapter.py"
      - ".codex/schemas/harness/agent-run.schema.json"
    must_not_route_to:
      - "workflow-loop-runner"
      - "plan-loop-term"
    notes: "Live run manifest bootstrap is harness implementation, not LoopRun execution."
  - request: "이 번들에서 tool class를 routine/risky/blocked로 보는 운영 카탈로그를 정리해줘"
    expected_primary_skill: "task-specific documentation"
    expected_attachments:
      - "workflow-rigor only if policy examples or rules are changed"
    must_read:
      - ".codex/docs/tool_hardening_profile.md"
      - ".codex/rules/default.rules"
      - ".codex/schemas/tools/tool-policy.schema.json"
    must_not_route_to:
      - "loop-readiness-router"
      - "workflow-loop-runner"
    notes: "Tool policy catalog explains operating boundaries; it does not replace host approval/rules."
  - request: "이 loop를 cron/webhook/queue로 계속 돌릴 수 있는지 runtime capability부터 판단해줘"
    expected_primary_skill: "loop-readiness-router"
    expected_route_class: "loop_readiness_contract_needed"
    expected_attachments:
      - "plan-loop-term only after runtime support and success criteria are contract-ready"
    must_read:
      - ".codex/docs/orchestration_capability_contract.md"
    must_not_route_to:
      - "workflow-loop-runner"
    notes: "General orchestration runtime must be verified or marked external_host_dependent/unsupported before execution claims."
  - request: "loop 실행 결과에서 Wiki Bank에 남길 개선 후보만 정리하고 accepted knowledge로는 올리지 마"
    expected_primary_skill: "workflow-loop-runner"
    expected_attachments:
      - "knowledge-base-maintenance only if user asks to review/promote candidates"
    must_not_route_to:
      - "knowledge-context-harness"
    notes: "Loop runner may emit feedback candidates but must not mutate accepted Wiki Bank knowledge."
  - request: "완료된 plan은 핵심 결정만 memory 후보로 남기고 다음부터 raw plan은 active context에서 빼줘"
    expected_primary_skill: "plan-spec-curator"
    expected_attachments: []
    must_read:
      - "target plan slice or active plan pointer"
    expected_default_exclude:
      - "full memory bank"
      - "all old plans"
      - "archived raw plans"
    must_not_route_to:
      - "plan-short-term-docs"
      - "memory-bank-update"
      - "coordination-brief"
    notes: "Closeout and active-context load policy are context lifecycle curation; actual memory mutation is separate."
  - request: "지침이 너무 길어졌으니 runtime에 넣을 것과 reference/archive로 뺄 것을 정리해줘"
    expected_primary_skill: "plan-spec-curator"
    expected_attachments: []
    must_read:
      - "current instruction/spec packet"
    expected_default_exclude:
      - "full chat history"
      - "full memory bank"
    must_not_route_to:
      - "analysis-codebase"
      - "plan-long-term-package"
    notes: "Instruction-bloat reduction creates a compact context packet, not a broad report."
  - request: "플랜이라는 단어가 무슨 뜻이야?"
    expected_primary_skill: null
    expected_route_class: "conceptual_explanation"
    expected_attachments: []
    must_not_route_to:
      - "plan-short-term-docs"
      - "plan-long-term-package"
    notes: "Casual word meaning does not create or sync a plan artifact."
  - request: "이 마이그레이션을 phase별 서브플랜 패키지로 만들어줘"
    expected_primary_skill: "plan-long-term-package"
    expected_attachments: []
    must_not_route_to:
      - "plan-short-term-docs"
    notes: "Package/phase artifact intent selects the heavy planning package."
  - request: "이 마이그레이션을 phase별 서브플랜 패키지로 만들고 각 phase의 loop term도 포함해줘"
    expected_primary_skill: "plan-long-term-package"
    expected_attachments:
      - "plan-loop-term"
    must_not_route_to:
      - "plan-short-term-docs"
    notes: "Broad multi-document package owns the work; loop terms are package sub-artifacts."
  - request: "이 repo 전체 코드베이스 분석 리포트를 만들어줘"
    expected_primary_skill: "analysis-codebase"
    expected_attachments: []
    must_not_route_to:
      - "analysis-bug"
    notes: "Repo-wide report artifact intent is explicit."
  - request: "이 diff 검토해줘"
    expected_primary_skill: null
    expected_route_class: "ordinary_review_or_task_specific_primary"
    expected_attachments: []
    must_not_route_to:
      - "analysis-codebase"
      - "plan-long-term-package"
    notes: "Attach report-critical only if critical, QA, blocker, risk, or validation framing is present."
  - request: "바뀐 부분만 읽기 쉽게 보여줘"
    expected_primary_skill: "report-diff"
    expected_attachments: []
    must_not_route_to:
      - "analysis-bug"
      - "analysis-codebase"
    notes: "Readable diff is output presentation, not root-cause analysis."
  - request: "srq로 완료 보고해"
    expected_primary_skill: null
    expected_route_class: "final_output_modifier"
    expected_attachments:
      - "report-qualitative"
    must_not_route_to:
      - "analysis-codebase"
    notes: "Legacy srq uses report-qualitative compact evidence report mode, not the full qualitative evaluation report."
  - request: "이 SKILL.md 초안을 정성평가 리포트로 작성해줘."
    expected_primary_skill: "report-qualitative"
    expected_route_class: "qualitative_evaluation_report"
    expected_attachments: []
    must_read:
      - "target artifact or artifact slice"
      - "evaluation goal"
      - "criteria or default qualitative criteria"
    must_not_route_to:
      - "report-critical"
      - "evaluation-harness"
      - "report-diff"
    notes: "Qualitative assessment/report intent routes to report-qualitative; it is not a critical QA gate or eval-case review."
  - request: "이 diff를 품질, 리스크, 개선안 중심으로 정성평가해줘."
    expected_primary_skill: "report-qualitative"
    expected_route_class: "qualitative_diff_evaluation"
    expected_attachments: []
    must_read:
      - "diff or change snapshot as artifact"
      - "evaluation goal"
      - "risk and improvement criteria"
    must_not_route_to:
      - "report-diff"
    notes: "Qualitative diff evaluation judges the diff as an artifact; it must not present changed-line diff blocks unless explicitly requested."
  - request: "이 프로젝트 룰을 메모리뱅크에 저장해줘"
    expected_primary_skill: "memory-bank-update"
    expected_attachments: []
    must_not_route_to:
      - "memory-bank-init"
      - "memory-bank-maintenance"
    notes: "Explicit persistent rule memory mutation."
  - request: "Wiki Bank Runtime Projection에서 이 작업용 Context Pack 만들어줘."
    expected_primary_skill: "knowledge-context-harness"
    expected_route_class: "knowledge_context_read"
    expected_attachments: []
    must_read:
      - "generated runtime projection index/cards"
      - "Context Pack validation command"
    expected_default_exclude:
      - "full Wiki Bank"
      - "accepted knowledge mutation"
      - "raw chat transcripts"
    must_not_route_to:
      - "memory-bank-update"
      - "knowledge-base-maintenance"
    notes: "Read-only Wiki Bank context supply; generated projection is consumed, not edited."
  - request: "이 feedback packet을 검토해서 Knowledge Store에 승격할지 판단해줘."
    expected_primary_skill: "knowledge-base-maintenance"
    expected_route_class: "knowledge_maintenance"
    expected_attachments:
      - "workflow-rigor optional for writes"
    must_read:
      - "feedback packet"
      - "source/claim/edge records under review"
    must_not_route_to:
      - "knowledge-context-harness"
      - "memory-bank-ingestion"
    notes: "Accepted knowledge mutation requires explicit maintenance/review, not context consumption or Memory Bank ingestion."
  - request: "간단히 이 파일 오타만 고쳐줘."
    expected_primary_skill: null
    expected_route_class: "ordinary_small_edit"
    expected_attachments: []
    expected_default_exclude:
      - "knowledge-context-harness"
      - "knowledge-base-maintenance"
      - "Memory Bank mutation"
    must_not_route_to:
      - "knowledge-context-harness"
      - "knowledge-base-maintenance"
    notes: "Simple local edits do not trigger Wiki Bank context supply."
  - request: "이번 답변만 짧게 해줘"
    expected_primary_skill: null
    expected_route_class: "one_turn_preference"
    expected_attachments: []
    must_not_route_to:
      - "memory-bank-init"
      - "memory-bank-update"
      - "memory-bank-correction-capture"
      - "memory-bank-maintenance"
      - "report-qualitative"
    notes: "One-turn preference must not become persistent memory."

  - request: "음성 향상 최신연구를 하고싶어. 다만 clean label이 clean하지 못하고 기존 discriminative 모델들이 over-denoising을 하면서 PESQ를 맞추고 있다는게 내 주장이야."
    expected_primary_skill: "research-router"
    expected_route_class: "research_evidence_first_planning"
    expected_next_skills:
      - "search-paper-evidence"
      - "research-hypothesis-planning"
    expected_reference:
      - "speech-enhancement-research"
    must_include:
      - "premise triage"
      - "evidence search or evidence-not-acquired state"
      - "user claim not treated as fact"
      - "checkpoint/baseline-first plan"
      - "progressive ablation ladder"
      - "loss budget"
    must_not_include:
      - "fabricated citations"
      - "direct assumption that the user claim is true"
      - "new training before evidence/checkpoint/baseline evaluation"
      - "multi-loss soup in the core experiment"
    notes: "In 6.0, latest/literature-backed speech research routes through evidence acquisition before final planning unless sufficient papers are provided."
  - request: "이 문제에는 어떤 알고리즘이 좋아?"
    expected_primary_skill: "analysis-algorithm"
    must_not_route_to:
      - "research-hypothesis-planning"
    notes: "Generic algorithm recommendation is not a research plan."
  - request: "이 loss 함수 구현하고 테스트까지 추가해줘."
    expected_primary_skill: null
    expected_route_class: "development_implementation"
    must_not_route_to:
      - "research-hypothesis-planning"
    notes: "Implementation of a chosen loss is a development task, not research hypothesis planning."
  - request: "이 플랜대로 구현해줘."
    expected_primary_skill: "workflow-plan-runner"
    expected_route_class: "approved_plan_execution"
    expected_attachments:
      - "workflow-rigor for medium/high-risk implementation"
      - "plan-short-term-docs only as secondary status sync when an active plan exists"
    must_read:
      - "active plan as task input"
      - "target source/test/config files"
      - "validation contract"
      - "execution-source sufficiency"
    must_not_route_to:
      - "plan-long-term-package"
      - "plan-spec-curator"
    must_not_complete_with:
      - "docs/plan-only diff"
      - "Markdown-only plan/status update"
    notes: "A plan implementation command consumes the plan through workflow-plan-runner and executes code work; plan synchronization is bookkeeping, not completion evidence. Output should include execution scope, batch plan, changed artifacts, validation per batch, and rollback/fallback if needed."
  - request: "이 스펙대로 Phase 1 초기 구현을 진행해줘."
    expected_primary_skill: "workflow-plan-runner"
    expected_attachments:
      - "workflow-rigor"
      - "workflow-validation as needed"
    must_read:
      - "approved spec or package slice"
      - "target source/test/config files"
    must_not_route_to:
      - "plan-long-term-package"
      - "coordination-brief as primary"
    notes: "Spec-driven waterfall-style implementation is execution, not plan/package creation."
  - request: "이 변경을 어떻게 검증할지 validation matrix만 짜줘."
    expected_primary_skill: "workflow-validation"
    expected_attachments: []
    must_read:
      - "changed artifact or planned change"
      - "success criteria"
      - "risk tier and available checks"
    must_not_route_to:
      - "evaluation-harness"
      - "report-critical"
    notes: "Product validation planning is workflow-validation, not skill-system eval or QA verdicting. Output should select the smallest meaningful risk-tiered check set."
  - request: "같은 테스트가 계속 실패해. fake fix 말고 원인 하나씩 격리하자."
    expected_primary_skill: "workflow-recovery"
    expected_attachments:
      - "analysis-bug optional for RCA"
      - "workflow-validation optional for revised checks"
    must_read:
      - "failing command or log"
      - "latest attempted fix"
      - "same or materially similar failure signature"
    must_not_route_to:
      - "plan-long-term-package"
      - "report-qualitative"
    notes: "Repeated failure loop selects recovery as primary only when a similar failure repeats after a fix/rerun or the user explicitly asks to stop fake fixes."
  - request: "이 모델 학습 파이프라인 구현 플랜을 짜줘."
    expected_primary_skill: null
    expected_route_class: "development_implementation_plan"
    must_not_route_to:
      - "research-hypothesis-planning"
    notes: "If the user asks to implement an already chosen pipeline, keep development mode."
  - request: "speech enhancement 최신 논문을 찾아서 gap과 연구 가설을 뽑아줘"
    expected_primary_skill: "research-router"
    expected_next_skills:
      - "search-paper-evidence"
      - "research-literature-ideation"
    expected_reference:
      - "speech-enhancement-research"
    notes: "Detailed research cluster routing is in .codex/research-routing.md."
  - request: "codex-research-lifecycle 스킬 그대로 설치해줘"
    expected_primary_skill: null
    expected_route_class: "blocked_monolithic_research_skill"
    must_not_create:
      - ".codex/skills/codex-research-lifecycle"
    notes: "Source archive is source material only; do not install as a monolithic skill."
  - request: "일반 웹앱 버그 수정해줘"
    expected_route_class: "development_implementation"
    must_not_load:
      - "speech-enhancement-research"
      - "research-router"
    notes: "Ordinary development must not load the research cluster."
```

## Agent Metadata Tradeoff
Current `agents/openai.yaml` metadata is conservative: specialist skills and heavy artifact generators use `allow_implicit_invocation: false` to prevent broad-trigger overactivation. The only current implicit exceptions are `analysis-router`, `research-router`, and `search-router`, backed by smoke/eval negative cases. Explicit aliases, Routing Cards, and this routing contract remain the primary activation path for all other skills.


## Group Alias Routing

User-facing skill families are defined in `docs/skill_registry.md` (the `family` column and Group Alias Map). This section defines only *when* group-selection mode is used and *which entry skill* each family routes to. Alias and display strings are not duplicated here; the registry Group Alias Map is their single source.

Trigger guard:
- Enter group-selection mode only when the request carries an explicit family-framing token (`스킬군`, `그룹`, `계열`, `group`, `family`) or an explicit family name.
- Do not enter group-selection mode for bare domain words like `분석`, `검토`, `보고`, `계획`; those route by the normal Route Matrix.

Family entry routing (Phase A):
| family | entry skill |
| --- | --- |
| `search` | `search-router` |
| `design` | `design-frontend` |
| `report` | `report-qualitative` (정성평가/보고) or `report-critical` (검토/QA/blocker) by intent |
| `research` | `research-router` |
| `analysis` | `analysis-router` / `analysis-domain-modeling` / `analysis-performance` / `analysis-codebase-design` / `analysis-architecture-deepening` by intent |
| `workflow` | `workflow-implementation` / `workflow-bug-fix` / `workflow-dependency-upgrade` / `workflow-source-maintenance` / `workflow-comment-maintenance` / `workflow-refactor-safely` / `workflow-rigor` / `workflow-minimal-implementation` / `workflow-plan-runner` / `workflow-validation` / `workflow-recovery` by intent |
| `coordination` | `coordination-brief` |
| `planning` | `plan-short-term-docs` / `plan-loop-term` / `plan-long-term-package` by intent |
| `loop` | `loop-readiness-router` / `loop-verifier-registry` / `workflow-loop-runner` by intent |
| `memory` | `memory-bank-harness` (read), `memory-bank-ingestion` (promotion), or explicit memory-mutation skills by intent |
| `evaluation` | `evaluation-harness` (case review) or `evaluation-usage-tracker` (usage telemetry) by intent |
| `skill_system` | `create-skill-pack` |

Evidence vs research boundary (mirrored rule; `research-routing.md` is Codex-only, so this boundary lives here so both Codex and Claude apply it):
- Cross-domain evidence search (papers, code, runtime, visual, memory) belongs to the `search` family; the `search` entry opens an evidence lane and `search-paper-evidence` provides paper evidence as support.
- The whole task routes to `research` (`research-router`) only when the user develops a scientific claim, hypothesis, experiment, ablation, manuscript, or publishability decision.
- Implementation/plan/algorithm requests that merely mention paper/loss/model/experiment keep their implementation/planning/analysis primary; research attaches only as a support evidence lane.

Phase B note:
- `analysis-router`, `research-router`, and `search-router` are the only selectively implicit entry routers. Specialist skills remain explicit-only unless future field feedback justifies another exception.
- `evaluation-usage-tracker` and `memory-bank-ingestion` remain experimental explicit-only skills.
- Loop engineering skills remain explicit/routing-controlled: readiness classification, verifier mapping, and loop execution are separate to avoid accidental long-running loops.
