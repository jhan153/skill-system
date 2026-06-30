---
name: analysis-domain-modeling
description: Analyze domain concepts, entity/value-object boundaries, state transitions, invariants, business rules, and naming language for software design. Use when a development task depends on clarifying the domain model before implementation or refactoring. Do not use for generic architecture review, full codebase reports, persistent glossary writing, or documentation-only work unless explicitly requested.
---

# Analysis Domain Modeling

## Routing Card
- role: primary
- intent_signature:
  - domain modeling
  - ubiquitous language
  - entity boundary
  - value object
  - aggregate boundary
  - invariant
  - business rule
  - state transition
  - domain concept
  - naming boundary
  - 도메인 모델링
  - 도메인 모델
  - 엔티티 경계
  - 값 객체
  - 상태 전이
  - 불변식
  - 업무 규칙
- use_when:
  - the user asks to clarify domain concepts, names, invariants, lifecycle states, or model boundaries.
  - implementation friction comes from confused terminology, leaky data shapes, or mixed domain concepts.
  - a feature, refactor, or API change needs a domain model decision before code changes.
- do_not_use_when:
  - the task is ordinary implementation with clear existing terminology; use `workflow-implementation`.
  - the task is generic architecture review or full codebase reporting; use `analysis-codebase-design`, `analysis-architecture-deepening`, or `analysis-codebase` by scope.
  - the question is a module/interface/seam decision rather than domain language; use `analysis-codebase-design`.
  - the user asks for persistent memory, glossary, ADR, or docs mutation without explicit write scope.
  - the user asks for documentation-only work without a development design dependency.
  - the task is pure research hypothesis planning, product strategy, or business ideation.
- expected_inputs:
  - domain area, user story, API/data model, entity, workflow, or naming concern
  - relevant source files, schemas, tests, docs, examples, or current terminology when available
  - explicit non-goals and write scope when documentation or code changes are requested
- expected_outputs:
  - domain vocabulary, concept boundaries, invariants, state model, naming decisions, code/design handoff, and unresolved questions
- context_targets:
  must_read:
    - current domain-modeling request
    - relevant model/schema/API/source surface or explicit `Unverified` gap
    - existing domain terms in nearby code or docs
  read_if_needed:
    - tests and fixtures that encode domain rules
    - database/API schemas
    - ADRs, glossary, or product docs explicitly referenced by the user
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated product docs
    - generated repo-wide reports
- risk_profile:
  reads:
    - targeted source, schemas, tests, fixtures, docs, and examples
  writes:
    - none by default; WRITE_CODEBASE or WRITE_DOCS only when the user explicitly asks to apply the model
  tools:
    - focused search, schema inspection, and targeted tests when domain rules need evidence
  sensitive_resources:
    - credentials default deny; avoid inspecting production data to infer domain rules
- entry_scene:
  - PREPARE

## Purpose
- Turn ambiguous domain language into code-ready concepts.
- Separate entities, value objects, states, commands, events, policies, and invariants.
- Produce implementation handoff without silently editing glossary, ADR, memory, or docs.

## Workflow
1. Collect current language: names in code, tests, schemas, docs, errors, and user wording.
2. Identify concept candidates and conflicts:
   - same word, different concepts
   - different words, same concept
   - data shape masquerading as domain concept
   - state name hiding a lifecycle transition
3. Classify the model:
   - entity: identity over time
   - value object: equality by value
   - state: lifecycle condition
   - command: user/system intent
   - event: fact that happened
   - policy/invariant: rule that must hold
4. State invariants and invalid states explicitly.
5. Propose naming and boundary decisions with code impact.
6. Hand off to `workflow-implementation`, `workflow-refactor-safely`, or `analysis-codebase-design` when changes are requested.

## Modeling Rules
- Prefer terms already used consistently in the codebase.
- When the code and user language conflict, surface the conflict instead of silently renaming.
- Do not invent business rules from names alone.
- Treat inferred rules as hypotheses until confirmed by tests, code paths, docs, or user input.
- Mark missing evidence `Unverified`.
- Make invalid states hard to represent when the target language/framework supports it without large churn.
- Do not write persistent glossary, ADR, memory, or wiki files unless explicitly requested.
- Prefer a bounded domain model note in the response over broad documentation edits.
- If implementation is requested after the model is clarified, hand off to `workflow-implementation` or `workflow-refactor-safely`.

## Output Contract
Return only the sections needed:
- `domain_area`
- `current_language`
- `concept_model`
- `invariants`
- `state_transitions`
- `naming_decisions`
- `implementation_handoff`
- `unverified_questions`

## Cross-Skill Boundaries
- `analysis-codebase-design` owns module boundaries, deep modules, seams, and adapters.
- `workflow-implementation` owns direct code changes from a selected model.
- `workflow-refactor-safely` owns behavior-preserving renames/extractions after the model is selected.
- `analysis-bug` owns current failure RCA when the issue starts from a broken behavior.
- Memory or knowledge skills own persistent memory/knowledge mutation when explicitly requested.

## Invocation Examples
Positive:
- "이 결제 상태 모델에서 entity/value object/invariant를 정리해줘."
- "API 이름이 헷갈려. 도메인 용어와 모델 경계를 잡아줘."
- "이 기능 구현 전에 도메인 상태 전이를 먼저 정리하자."

Negative:
- "이 모듈 interface를 deep module 관점에서 설계해줘." -> `analysis-codebase-design`
- "이 이름 변경을 바로 코드에 반영해줘." -> `workflow-refactor-safely`
- "이 버그 원인 분석해줘." -> `analysis-bug`
