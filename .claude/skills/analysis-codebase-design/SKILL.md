---
name: analysis-codebase-design
description: Codebase design analysis for module boundaries, deep modules, interfaces, seams, adapters, dependency direction, and testability. Use when Codex must judge or propose a targeted code structure change before implementation, without producing a repo-wide report artifact.
---

# Analysis Codebase Design

## Routing Card
- role: primary
- intent_signature:
  - codebase design
  - module boundary
  - deep module
  - interface design
  - seam design
  - adapter boundary
  - 코드베이스 설계
  - 딥모듈
- use_when:
  - the user asks for module, interface, seam, dependency, adapter, or codebase design judgment.
  - implementation pressure suggests a structural change may reduce real complexity.
  - a bug fix or feature needs a design decision before broad refactoring.
- do_not_use_when:
  - the user asks for a repo-wide report artifact; use `analysis-codebase`.
  - the task is ordinary implementation with an obvious local change; use `workflow-implementation`.
  - the task is first-pass bug RCA; use `analysis-bug`.
  - the user wants pure domain glossary or ADR maintenance without code structure decisions.
- expected_inputs:
  - design pressure, change friction, testing pain, coupling concern, or target module
  - relevant source files, call sites, tests, and existing local patterns
  - explicit constraints and non-goals when available
- expected_outputs:
  - current structure, design pressure, candidate design moves, abstraction gate result, recommended boundary, validation or implementation handoff
- context_targets:
  must_read:
    - current design question or implementation pressure
    - target module/interface/call sites
    - local tests or usage sites when testability is part of the question
  read_if_needed:
    - nearby architecture docs or ADRs
    - package/module manifests
    - related bug or implementation evidence
  do_not_load_by_default:
    - full repo
    - full memory bank
    - generated repo-wide report artifacts
    - unrelated domain documents
- risk_profile:
  reads:
    - targeted source, tests, call sites, docs, and dependency signals
  writes:
    - none by default; WRITE_CODEBASE only through an implementation owner after the design is selected
  tools:
    - focused search, static checks, dependency inspection, and targeted tests when needed for evidence
  sensitive_resources:
    - credentials default deny; design analysis should not inspect secrets
- entry_scene:
  - PREPARE

## Purpose
- Make targeted codebase design decisions before or during implementation.
- Prefer deep modules: small stable interfaces that hide real complexity and reduce caller knowledge.
- Prevent speculative abstraction by requiring current leverage, locality, or testability evidence.

## Design Vocabulary
- Module: a boundary that hides decisions, data shape, side effects, or policy from callers.
- Interface: the smallest stable surface callers need to use the module.
- Deep module: a module whose interface is simpler than the complexity it hides.
- Shallow module: a wrapper or layer whose interface mostly repeats its implementation.
- Seam: a boundary where behavior can be substituted, tested, or isolated without leaking policy.
- Adapter: a boundary that isolates external APIs, libraries, protocols, storage, or runtime services.

## Workflow
1. Name the design pressure: change friction, duplicated policy, test pain, unstable dependency, caller knowledge, or concept mismatch.
2. Map the current boundary: callers, callees, data crossing the boundary, side effects, and tests.
3. Evaluate depth: interface size, hidden complexity, locality, dependency direction, and deletion potential.
4. Compare 2-3 design moves:
   - keep local change
   - deepen existing module
   - extract a seam or adapter
   - collapse a shallow wrapper
   - move policy toward the owning concept
5. Run the abstraction gate before recommending new structure.
6. Return the selected design and the smallest implementation handoff.

## Abstraction Gate
Approve a new abstraction only when at least one is true:
- it hides current complexity from multiple callers or a high-churn caller.
- it protects the codebase from an unstable external dependency.
- it creates a test seam for behavior that is otherwise expensive or brittle to verify.
- it moves policy to the module that owns the concept.
- it deletes more knowledge from callers than it adds in new files or interfaces.

Reject or defer when:
- there is only one implementation and no concrete test seam or external boundary.
- the proposed interface only delegates to another object.
- the design primarily prepares for possible future features.
- the added layer would make the current change harder to validate.

## Output Contract
Return only the sections needed:
- `design_pressure`
- `current_boundary`
- `candidate_moves`
- `abstraction_gate`
- `recommended_design`
- `implementation_handoff`
- `validation_notes`
- `risks`

## Cross-Skill Boundaries
- `workflow-implementation` owns applying the selected design in code.
- `workflow-bug-fix` owns concrete failure repair; attach this skill only for structural bug fixes.
- `analysis-architecture-deepening` owns scanning for multiple deepening opportunities.
- `analysis-codebase` owns repo-wide architecture/report artifacts.
- `workflow-minimal-implementation` owns YAGNI pressure and should challenge speculative layers.

## Invocation Examples
Positive:
- "이 모듈 deep module로 만들려면 어떤 interface가 맞아?"
- "이 adapter를 만들 가치가 있는지 설계 판단해줘."
- "테스트가 어려운데 seam을 어디에 둘지 봐줘."

Negative:
- "이 기능 그냥 구현해줘." -> `workflow-implementation`
- "repo-wide architecture report 만들어줘." -> `analysis-codebase`
- "도메인 용어집을 정리해줘." -> domain-modeling or docs workflow, not this skill
