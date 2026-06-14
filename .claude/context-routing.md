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
| bug diagnosis | `deep-analysis-workflow` -> `deep-bug-analysis` | `strict-evidence-driven-reporting-workflow` only if implementation/risk is active | symptom, repro, relevant files, logs | full repo report |
| algorithm proposal | `deep-analysis-workflow` -> `deep-algorithm-proposal` | `strict-response-quality` only for formal output | constraints, metrics, candidates | full repo or memory |
| research / scientific workflow | `research-router` | selected narrow research cluster skill; `plan-doc-workflow` only for explicit persisted `docs/plan` artifact | research request, stage hints, provided artifacts, `.codex/research-routing.md` when needed | full repo, full memory bank, `codebase-intel-report`, `phase-subplan-workflow`, experiment scaffold unless explicitly requested |
| implementation | task-specific primary | `strict-evidence-driven-reporting-workflow` for medium/high-risk changes | repo `AGENTS.md`, relevant files, validation | unrelated docs |
| plan document | `plan-doc-workflow` | `agent-critical-review` only for QA/review | active plan, plan template | phase package |
| context/spec lifecycle curation | `spec-and-plan-curator` | `agent-critical-review` only for QA/review | current goal or task, candidate plan/spec slice, lifecycle state when available | full memory bank, all old plans, archived raw plans, full chat history |
| phase package | `phase-subplan-workflow` | `strict-evidence-driven-reporting-workflow` if execution risk is active | prior reports, templates | lightweight plan only |
| codebase report | `codebase-intel-report` | `agent-critical-review` after report if requested | repo root, scripts, tracked files | single-bug workflow |
| diff presentation | `readable-diff-report` | `agent-critical-review` only if verdict requested | verified diff or snapshot | root-cause workflow |
| critical review | `agent-critical-review` | `strict-response-quality` if formal report requested | artifact slice, goal, evidence anchors | full history |
| memory operation | `memory-bank-init`, `memory-bank-update`, `memory-bank-correction-capture`, or `memory-bank-maintenance` | none by default | matching active memory cards and target memory files | unrelated memory |
| skill lifecycle | `create-skill-pack` for user-managed custom skills under `.codex/skills/*` excluding `.system` | `agent-critical-review` optional after draft | lifecycle request, target custom skill, one or two adjacent examples | `.system`, unrelated repo files, full skill library |

Development/implementation requests keep the existing implementation, bug, algorithm, or plan skills as primary and follow concrete user requirements as task specifications. Do not route to the research cluster merely because a development request mentions model, metric, experiment, loss, or training. Detailed Research Cluster routing lives in `.codex/research-routing.md`.

Aliases may remain in user-facing language, but routing docs should show actual skill IDs. Use system-provided `skill-creator` only when the runtime explicitly exposes it and the user asks for that platform-specific path; otherwise `create-skill-pack` owns user-managed custom `.codex` skill lifecycle work, including reference packs, hardening, migration, metadata, routing registration, smoke tests, and deprecation notes. `.system` skills are outside this lifecycle.

## Design Cluster Routing

Design specialists are narrow. `design-to-frontend` remains the primary implementation owner for concrete visual artifacts. Evidence gates and analysis skills should not take over code changes unless the user explicitly asks for that kind of artifact.

| Request type | Primary skill | Supporting skill(s) | Must not trigger as primary |
| --- | --- | --- | --- |
| concrete visual artifact to repo UI code | `design-to-frontend` | token/component/visual/a11y gates when evidence exists | `ui-reference-decomposer`, `layout-constraint-translator` |
| visual reference breakdown without code | `ui-reference-decomposer` | `layout-constraint-translator` if constraints dominate | `design-to-frontend` |
| Auto Layout/flex/grid/sizing/overflow/breakpoint translation | `layout-constraint-translator` | `visual-regression-harness` only after rendered evidence exists | `design-to-frontend` |
| explicitly invoked mobile/native screen implementation | `mobile-screen-implementation` | `design-to-frontend`, `visual-regression-harness`, `accessibility-audit-harness` | `dashboard-ui-implementation`, `section-based-web-implementation` |
| explicitly invoked dashboard/admin/analytics implementation | `dashboard-ui-implementation` | `design-to-frontend`, `component-contract-mapper`, `visual-regression-harness`, `accessibility-audit-harness` | `mobile-screen-implementation`, `section-based-web-implementation` |
| explicitly invoked section-based web implementation | `section-based-web-implementation` | `design-to-frontend`, `visual-regression-harness`, `accessibility-audit-harness` | `mobile-screen-implementation`, `dashboard-ui-implementation` |
| token source normalization or token gaps | `design-token-pipeline` | `component-contract-mapper` if component styles are involved | `design-to-frontend` |
| design component to repo component/state mapping | `component-contract-mapper` | `design-token-pipeline`, `accessibility-audit-harness` when relevant | `visual-regression-harness` |
| rendered screenshot, nonblank, viewport, or visual diff evidence | `visual-regression-harness` | `accessibility-audit-harness` for focus/contrast/readability | `design-to-frontend` |
| keyboard/focus/semantic/contrast/target-size/readability evidence | `accessibility-audit-harness` | `visual-regression-harness` for rendered screenshot evidence | `design-to-frontend` |

Design cluster conservative defaults:
- New or recently hardened design skills keep `allow_implicit_invocation: false` until route smoke tests and field feedback justify broader routing.
- `ui-reference-decomposer` and `layout-constraint-translator` are operational `experimental` analysis skills, but should remain explicit or clearly analysis-intent routed until field feedback exists.
- Surface-specific implementation skills are active `experimental` explicit-only surface specialists; they do not auto-displace `design-to-frontend` for generic visual implementation.
- Each new design skill needs at least three `should_not_trigger` cases before implicit invocation can be reconsidered.

## Routing Card Audit Shape
Each user-managed custom `SKILL.md` Routing Card, excluding `.codex/skills/.system/**`, should keep these Markdown fields in this order unless a local reason exists: `role`, `intent_signature`, `use_when`, `do_not_use_when`, `expected_inputs`, `expected_outputs`, `context_targets` with `must_read`, `read_if_needed`, `do_not_load_by_default`, `risk_profile` with `reads`, `writes`, `tools`, `sensitive_resources`, and `entry_scene`.

## Multi-Host Portability
This `.codex` setup is used on multiple host environments. Multiple host-specific homes may be valid. Reusable skills and automations should prefer `$CODEX_HOME`, `$HOME/.codex`, `${CODEX_HOME:-$HOME/.codex}`, or relative paths. Do not collapse host-specific paths to a single home directory.

Path classification:
- Trusted project paths in `config.toml` may be host-specific and should coexist when intentional.
- Host-specific project rules in global rules must stay prompt-gated; repeated repo workflows belong in repo-level policy.
- Reusable skill instructions, automation prompts, scripts, and examples should not hardcode one user home.
- Historical notes may mention old host paths; add clarification instead of rewriting history.


## Packaging Hygiene
Future settings archives should exclude package noise: `.DS_Store`, `__MACOSX/*`, and `*/._*`. Do not treat `.codex/skills/.system` as package noise.

```bash
zip -r Settings5.9.zip . -x "*.DS_Store" "__MACOSX/*" "*/._*"
```

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
      - "codebase-intel-report"
      - "phase-subplan-workflow"
    notes: "Skill lifecycle creation, not repo-wide reporting or planning package generation."
  - request: "기존 deep-bug-analysis 스킬의 Routing Card와 Risk Boundary를 보강해줘"
    expected_primary_skill: "create-skill-pack"
    expected_mode: "harden_existing_skill"
    target_skill: "deep-bug-analysis"
    must_read:
      - "skills/deep-bug-analysis/SKILL.md"
    exclude_as_primary_skill:
      - "deep-bug-analysis"
    expected_attachments:
      - "agent-critical-review optional after draft"
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
      - "codebase-intel-report"
    notes: "Reference-only packs prefer `.codex/references/{reference-pack-id}/` and are not route-registered as skills."
  - request: "스킬이란 개념이 뭐야?"
    expected_primary_skill: null
    expected_route_class: "conceptual_explanation"
    expected_attachments: []
    must_not_route_to:
      - "create-skill-pack"
    notes: "Conceptual explanation does not create or modify skill artifacts."
  - request: "deep-bug-analysis로 이 버그 분석해줘"
    expected_primary_skill: "deep-bug-analysis"
    expected_attachments: []
    must_not_route_to:
      - "create-skill-pack"
    notes: "Executing a skill is not creating or hardening a skill."
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
      - "codebase-intel-report"
    notes: "Routing registration and smoke tests are skill lifecycle work."
  - request: ".system 스킬도 Routing Card 보강해줘"
    expected_primary_skill: null
    expected_route_class: "out_of_scope_system_managed_skill"
    expected_attachments: []
    must_not_route_to:
      - "create-skill-pack"
    notes: "`.codex/skills/.system` is Codex app-managed and outside custom skill lifecycle scope."
  - request: "이 버그가 왜 반복되는지 원인 분석해줘"
    expected_primary_skill: "deep-bug-analysis"
    expected_route_class: "routed_by_deep-analysis-workflow"
    expected_attachments: []
    must_not_route_to:
      - "codebase-intel-report"
      - "phase-subplan-workflow"
    notes: "Bug diagnosis is point analysis, not repo-wide reporting."
  - request: "이 문제는 어떤 알고리즘/접근이 제일 맞아?"
    expected_primary_skill: "deep-algorithm-proposal"
    expected_route_class: "routed_by_deep-analysis-workflow"
    expected_attachments: []
    must_not_route_to:
      - "codebase-intel-report"
      - "memory-bank-init"
      - "memory-bank-update"
      - "memory-bank-correction-capture"
      - "memory-bank-maintenance"
    notes: "Recommendation intent selects the algorithm primary, not bug RCA."
  - request: "이 개념을 탐색해보자"
    expected_primary_skill: null
    expected_route_class: "casual_exploration"
    expected_attachments: []
    must_not_route_to:
      - "deep-analysis-workflow"
    notes: "Casual exploration needs no deep-analysis router unless deep technical diagnosis or recommendation intent is present."
  - request: "이 작업을 docs/plan 플랜 문서로 만들어줘"
    expected_primary_skill: "plan-doc-workflow"
    expected_attachments: []
    must_not_route_to:
      - "phase-subplan-workflow"
    notes: "Persisted docs/plan artifact intent is explicit."
  - request: "완료된 plan은 핵심 결정만 memory 후보로 남기고 다음부터 raw plan은 active context에서 빼줘"
    expected_primary_skill: "spec-and-plan-curator"
    expected_attachments: []
    must_read:
      - "target plan slice or active plan pointer"
    expected_default_exclude:
      - "full memory bank"
      - "all old plans"
      - "archived raw plans"
    must_not_route_to:
      - "plan-doc-workflow"
      - "memory-bank-update"
      - "goal-workflow-orchestrator"
    notes: "Closeout and active-context load policy are context lifecycle curation; actual memory mutation is separate."
  - request: "지침이 너무 길어졌으니 runtime에 넣을 것과 reference/archive로 뺄 것을 정리해줘"
    expected_primary_skill: "spec-and-plan-curator"
    expected_attachments: []
    must_read:
      - "current instruction/spec packet"
    expected_default_exclude:
      - "full chat history"
      - "full memory bank"
    must_not_route_to:
      - "codebase-intel-report"
      - "phase-subplan-workflow"
    notes: "Instruction-bloat reduction creates a compact context packet, not a broad report."
  - request: "플랜이라는 단어가 무슨 뜻이야?"
    expected_primary_skill: null
    expected_route_class: "conceptual_explanation"
    expected_attachments: []
    must_not_route_to:
      - "plan-doc-workflow"
      - "phase-subplan-workflow"
    notes: "Casual word meaning does not create or sync a plan artifact."
  - request: "이 마이그레이션을 phase별 서브플랜 패키지로 만들어줘"
    expected_primary_skill: "phase-subplan-workflow"
    expected_attachments: []
    must_not_route_to:
      - "plan-doc-workflow"
    notes: "Package/phase artifact intent selects the heavy planning package."
  - request: "이 repo 전체 코드베이스 분석 리포트를 만들어줘"
    expected_primary_skill: "codebase-intel-report"
    expected_attachments: []
    must_not_route_to:
      - "deep-bug-analysis"
    notes: "Repo-wide report artifact intent is explicit."
  - request: "이 diff 검토해줘"
    expected_primary_skill: null
    expected_route_class: "ordinary_review_or_task_specific_primary"
    expected_attachments: []
    must_not_route_to:
      - "codebase-intel-report"
      - "phase-subplan-workflow"
    notes: "Attach agent-critical-review only if critical, QA, blocker, risk, or validation framing is present."
  - request: "바뀐 부분만 읽기 쉽게 보여줘"
    expected_primary_skill: "readable-diff-report"
    expected_attachments: []
    must_not_route_to:
      - "deep-bug-analysis"
      - "codebase-intel-report"
    notes: "Readable diff is output presentation, not root-cause analysis."
  - request: "srq로 완료 보고해"
    expected_primary_skill: null
    expected_route_class: "final_output_modifier"
    expected_attachments:
      - "strict-response-quality"
    must_not_route_to:
      - "codebase-intel-report"
    notes: "Formal output modifier attaches to the final report shape."
  - request: "이 프로젝트 룰을 메모리뱅크에 저장해줘"
    expected_primary_skill: "memory-bank-update"
    expected_attachments: []
    must_not_route_to:
      - "memory-bank-init"
      - "memory-bank-maintenance"
    notes: "Explicit persistent rule memory mutation."
  - request: "이번 답변만 짧게 해줘"
    expected_primary_skill: null
    expected_route_class: "one_turn_preference"
    expected_attachments: []
    must_not_route_to:
      - "memory-bank-init"
      - "memory-bank-update"
      - "memory-bank-correction-capture"
      - "memory-bank-maintenance"
      - "strict-response-quality"
    notes: "One-turn preference must not become persistent memory."

  - request: "음성 향상 최신연구를 하고싶어. 다만 clean label이 clean하지 못하고 기존 discriminative 모델들이 over-denoising을 하면서 PESQ를 맞추고 있다는게 내 주장이야."
    expected_primary_skill: "research-router"
    expected_route_class: "research_evidence_first_planning"
    expected_next_skills:
      - "research-paper-evidence-search"
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
    expected_primary_skill: "deep-algorithm-proposal"
    must_not_route_to:
      - "research-hypothesis-planning"
    notes: "Generic algorithm recommendation is not a research plan."
  - request: "이 loss 함수 구현하고 테스트까지 추가해줘."
    expected_primary_skill: null
    expected_route_class: "development_implementation"
    must_not_route_to:
      - "research-hypothesis-planning"
    notes: "Implementation of a chosen loss is a development task, not research hypothesis planning."
  - request: "이 모델 학습 파이프라인 구현 플랜을 짜줘."
    expected_primary_skill: null
    expected_route_class: "development_implementation_plan"
    must_not_route_to:
      - "research-hypothesis-planning"
    notes: "If the user asks to implement an already chosen pipeline, keep development mode."
  - request: "speech enhancement 최신 논문을 찾아서 gap과 연구 가설을 뽑아줘"
    expected_primary_skill: "research-router"
    expected_next_skills:
      - "research-paper-evidence-search"
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
Current `agents/openai.yaml` metadata is conservative: most custom skills use `allow_implicit_invocation: false` to prevent broad-trigger overactivation. Explicit aliases, Routing Cards, and this routing contract remain the primary activation path. If real usage shows under-activation, enable implicit invocation only for narrow router or primary skills after smoke-test validation. Heavy artifact generators must stay non-implicit.
